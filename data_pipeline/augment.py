#!/usr/bin/env python3
"""MM electronics defect-detection augmentation (image + bbox together).

Usage:
    python augment.py MM_Augmentation_Training_Data.json out_dir

Deps: numpy, opencv-python (cv2). Everything else is stdlib.

Pipeline per derived image
  1. one random affine (hflip, rotation, scale, translate) -> applied to image AND box corners
  2. box policy (see CONFIG): if ANY defect box would be lost/too small/too cut, the whole
     sample is rejected and re-drawn, so a defect never stays in the photo without its label
  3. random photometric changes (brightness/contrast, gamma, hue/sat, noise, blur, JPEG)
Seeded: every derived image has its own seed = BASE_SEED + source_id*1000 + k.
"""
import base64, csv, hashlib, json, sys
from pathlib import Path
import cv2
import numpy as np

CONFIG = {
    "base_seed": 20261021,
    "derived_per_source": 10,
    # class 2 (porosity) has only 1 box in the whole set -> give its source more derivatives
    "derived_per_class_override": {2: 20},
    "hflip_p": 0.5,
    "rotation_deg": 12.0,          # uniform(-12, 12); hull of rotated box inflates a little
    "scale_range": [0.80, 1.20],
    "translate_frac": 0.10,        # of width / height
    "border": "constant_gray_114", # NOT reflect/replicate: would duplicate defects without labels
    "box_policy": {
        "min_visible_area_ratio": 0.60,  # clipped area / unclipped transformed area
        "min_side_px": 8,                # after clipping
        "on_violation": "reject_whole_sample_and_resample",
        "max_resample_tries": 50,
    },
    "photometric": {
        "brightness_beta": [-30, 30],
        "contrast_alpha": [0.80, 1.25],
        "gamma": [0.80, 1.25],
        "hue_shift_deg": [-6, 6],      # small: defect colour is a cue
        "saturation_scale": [0.85, 1.15],
        "gauss_noise_sigma": [0, 6],
        "gauss_blur_p": 0.25, "gauss_blur_sigma": [0.4, 1.2],
        "jpeg_p": 0.5, "jpeg_quality": [55, 92],
    },
}


def sha256(b): return hashlib.sha256(b).hexdigest()


def affine_matrix(w, h, flip, angle, scale, tx, ty):
    cx, cy = w / 2.0, h / 2.0
    M = np.eye(3)
    if flip:
        M = np.array([[-1, 0, w], [0, 1, 0], [0, 0, 1]], float) @ M
    R = cv2.getRotationMatrix2D((cx, cy), angle, scale)  # +angle = counter-clockwise on screen
    M = np.vstack([R, [0, 0, 1]]) @ M
    M = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], float) @ M
    return M


def transform_box(box, M, w, h, pol):
    x1, y1, x2, y2 = box
    pts = np.array([[x1, y1, 1], [x2, y1, 1], [x2, y2, 1], [x1, y2, 1]], float).T
    q = (M @ pts)[:2]
    nx1, ny1, nx2, ny2 = q[0].min(), q[1].min(), q[0].max(), q[1].max()
    full = max(nx2 - nx1, 1e-6) * max(ny2 - ny1, 1e-6)
    cx1, cy1, cx2, cy2 = max(nx1, 0), max(ny1, 0), min(nx2, w), min(ny2, h)
    cw, ch = cx2 - cx1, cy2 - cy1
    if cw <= 0 or ch <= 0:
        return None, "outside"
    if (cw * ch) / full < pol["min_visible_area_ratio"]:
        return None, "too_cut"
    if min(cw, ch) < pol["min_side_px"]:
        return None, "too_small"
    return [cx1, cy1, cx2, cy2], "ok"


def photometric(img, rng, P):
    log = {}
    f = img.astype(np.float32)
    a = rng.uniform(*P["contrast_alpha"]); b = rng.uniform(*P["brightness_beta"])
    f = np.clip(f * a + b, 0, 255); log["contrast_alpha"] = round(a, 3); log["brightness_beta"] = round(b, 1)
    g = rng.uniform(*P["gamma"])
    f = 255.0 * (f / 255.0) ** g; log["gamma"] = round(g, 3)
    hsv = cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    dh = rng.uniform(*P["hue_shift_deg"]); ss = rng.uniform(*P["saturation_scale"])
    hsv[..., 0] = (hsv[..., 0] + dh / 2.0) % 180; hsv[..., 1] = np.clip(hsv[..., 1] * ss, 0, 255)
    f = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    log["hue_shift_deg"] = round(dh, 2); log["saturation_scale"] = round(ss, 3)
    sig = rng.uniform(*P["gauss_noise_sigma"])
    if sig > 0.5:
        f += rng.normal(0, sig, f.shape); log["gauss_noise_sigma"] = round(sig, 2)
    out = np.clip(f, 0, 255).astype(np.uint8)
    if rng.random() < P["gauss_blur_p"]:
        s = rng.uniform(*P["gauss_blur_sigma"]); out = cv2.GaussianBlur(out, (0, 0), s)
        log["gauss_blur_sigma"] = round(s, 2)
    q = None
    if rng.random() < P["jpeg_p"]:
        q = int(rng.integers(P["jpeg_quality"][0], P["jpeg_quality"][1] + 1))
        log["jpeg_quality"] = q
    return out, log, q


def main(src, out_dir):
    bundle = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(out_dir)
    for d in ("images/train", "labels/train", "overlays"):
        (out / d).mkdir(parents=True, exist_ok=True)

    guard_ids = {g["source_image_id"] for g in bundle["held_out_validation_guard"]}
    guard_sha = {g["image_sha256"] for g in bundle["held_out_validation_guard"]}
    cats = bundle["categories"]; cname = {c["id"]: c["name"] for c in cats}
    pol, P = CONFIG["box_policy"], CONFIG["photometric"]

    coco = {"info": {"description": "MM electronics augmented training set", "config": CONFIG},
            "images": [], "annotations": [], "categories": [{"id": c["id"], "name": c["name"]} for c in cats]}
    manifest = []
    img_id = ann_id = 0

    def add(file_name, img, boxes, cls, meta):
        nonlocal img_id, ann_id
        h, w = img.shape[:2]
        img_id += 1
        coco["images"].append({"id": img_id, "file_name": "images/train/" + file_name, "width": w, "height": h,
                               "source_image_id": meta["source_image_id"], "is_augmented": meta["is_augmented"]})
        lines = []
        for (x1, y1, x2, y2), c in zip(boxes, cls):
            bw, bh = x2 - x1, y2 - y1
            lines.append(f"{c} {(x1 + bw / 2) / w:.8f} {(y1 + bh / 2) / h:.8f} {bw / w:.8f} {bh / h:.8f}")
            ann_id += 1
            coco["annotations"].append({"id": ann_id, "image_id": img_id, "category_id": c,
                                        "bbox": [round(x1, 2), round(y1, 2), round(bw, 2), round(bh, 2)],
                                        "area": round(bw * bh, 2), "iscrowd": 0})
        (out / "labels/train" / (Path(file_name).stem + ".txt")).write_text("\n".join(lines) + "\n", encoding="utf-8")
        manifest.append({"image_file": file_name, "image_id": img_id, "n_boxes": len(boxes), **meta})

    for item in bundle["images"]:
        sid = item["source_image_id"]
        assert sid not in guard_ids, f"held-out image in training list: {sid}"
        raw = base64.b64decode(item["image_base64"], validate=True)
        assert sha256(raw) == item["image_sha256"], f"sha256 mismatch {sid}"
        assert sha256(raw) not in guard_sha
        img0 = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        h, w = img0.shape[:2]
        assert (w, h) == (item["width"], item["height"])
        boxes0 = [[float(v) for v in a["bbox_xyxy_pixels"]] for a in item["annotations"]]
        cls0 = [a["category_id"] for a in item["annotations"]]

        # original copy (untouched pixels, labels from the bundle)
        (out / "images/train" / item["file_name"]).write_bytes(raw)
        add(item["file_name"], img0, boxes0, cls0,
            {"source_image_id": sid, "is_augmented": False, "seed": None, "transforms": "original",
             "image_sha256": item["image_sha256"]})

        n = CONFIG["derived_per_source"]
        for c in cls0:
            n = max(n, CONFIG["derived_per_class_override"].get(c, 0))
        for k in range(1, n + 1):
            seed = CONFIG["base_seed"] + item["id"] * 1000 + k
            rng = np.random.default_rng(seed)
            tries = rejected = 0
            reasons = {}
            while True:
                tries += 1
                if tries > pol["max_resample_tries"]:
                    raise RuntimeError(f"cannot find valid transform for {sid} k={k}")
                flip = bool(rng.random() < CONFIG["hflip_p"])
                ang = float(rng.uniform(-CONFIG["rotation_deg"], CONFIG["rotation_deg"]))
                sc = float(rng.uniform(*CONFIG["scale_range"]))
                tx = float(rng.uniform(-CONFIG["translate_frac"], CONFIG["translate_frac"]) * w)
                ty = float(rng.uniform(-CONFIG["translate_frac"], CONFIG["translate_frac"]) * h)
                M = affine_matrix(w, h, flip, ang, sc, tx, ty)
                new, bad = [], None
                for bx in boxes0:
                    nb, why = transform_box(bx, M, w, h, pol)
                    if nb is None:
                        bad = why; break
                    new.append(nb)
                if bad:
                    reasons[bad] = reasons.get(bad, 0) + 1; rejected += 1
                    continue
                break
            warped = cv2.warpAffine(img0, M[:2], (w, h), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=(114, 114, 114))
            aug, plog, q = photometric(warped, rng, P)
            stem = f"{Path(item['file_name']).stem}__aug{k:02d}"
            if q is not None:
                fn = stem + ".jpg"
                ok, buf = cv2.imencode(".jpg", aug, [cv2.IMWRITE_JPEG_QUALITY, q]); assert ok
                (out / "images/train" / fn).write_bytes(buf.tobytes())
                aug = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            else:
                fn = stem + ".png"; cv2.imwrite(str(out / "images/train" / fn), aug)
            tf = {"hflip": flip, "rotation_deg": round(ang, 2), "scale": round(sc, 3),
                  "tx_px": round(tx, 1), "ty_px": round(ty, 1), **plog}
            add(fn, aug, new, cls0,
                {"source_image_id": sid, "is_augmented": True, "seed": seed,
                 "transforms": json.dumps(tf, ensure_ascii=False),
                 "resample_rejections": rejected, "rejection_reasons": json.dumps(reasons),
                 "image_sha256": None})

    (out / "annotations_coco.json").write_text(json.dumps(coco, ensure_ascii=False, indent=1), encoding="utf-8")
    keys = ["image_id", "image_file", "source_image_id", "is_augmented", "n_boxes", "seed", "transforms",
            "resample_rejections", "rejection_reasons", "image_sha256"]
    with open(out / "manifest.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); wr.writeheader(); wr.writerows(manifest)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "augmentation_config.json").write_text(json.dumps(CONFIG, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "dataset.yaml").write_text(
        "# NOTE: train only. Validation must come from held-out originals, never from derivatives of these sources.\n"
        "path: .\ntrain: images/train\nval: null  # fill with held-out validation images\n"
        "names:\n" + "".join(f"  {c['id']}: {c['name']}\n" for c in cats), encoding="utf-8")

    n_orig = sum(1 for m in manifest if not m["is_augmented"])
    n_aug = len(manifest) - n_orig
    per_cls = {}
    for a in coco["annotations"]:
        per_cls[cname[a["category_id"]]] = per_cls.get(cname[a["category_id"]], 0) + 1
    print(json.dumps({"originals": n_orig, "derived": n_aug, "total_images": len(manifest),
                      "total_boxes": len(coco["annotations"]), "boxes_per_class": per_cls}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "augmented_data")
