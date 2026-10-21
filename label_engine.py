"""Content-based source label lookup and local visual-reference retrieval.

Only identical decoded RGB pixels can inherit a source annotation. Similarity
retrieval returns examples, never a new image's ground-truth class or boxes.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
ANNOTATIONS = ROOT / 'annotations'
RECORDS = json.loads((ANNOTATIONS / 'records.json').read_text(encoding='utf-8'))['images']


def pixels(image):
    image = ImageOps.exif_transpose(image).convert('RGB')
    header = f'{image.width}:{image.height}:RGB:'.encode('ascii')
    return hashlib.sha256(header + image.tobytes()).hexdigest()


def feature(image):
    """A deterministic edge/gradient descriptor; not a trained type classifier."""
    gray = cv2.cvtColor(np.asarray(image.convert('RGB')), cv2.COLOR_RGB2GRAY)
    if float(gray.std()) < 3:
        return None
    gray = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
    bins = (angle / 45).astype(int) % 8
    hist = []
    for y in range(0, 64, 16):
        for x in range(0, 64, 16):
            h = np.bincount(bins[y:y+16, x:x+16].ravel(),
                            weights=mag[y:y+16, x:x+16].ravel(), minlength=8)
            hist.extend(h / (np.linalg.norm(h) + 1e-8))
    edges = cv2.Canny(gray, 60, 140)
    small = cv2.resize(edges, (16, 16), interpolation=cv2.INTER_AREA).astype(float).ravel()
    h = np.asarray(hist)
    f = np.concatenate((h / (np.linalg.norm(h) + 1e-8),
                        small / (np.linalg.norm(small) + 1e-8)))
    return f / (np.linalg.norm(f) + 1e-8)


def context_crop(image, box):
    x1, y1, x2, y2 = box
    pad = max(x2-x1, y2-y1) * .3
    return image.crop((max(0, int(x1-pad)), max(0, int(y1-pad)),
                       min(image.width, int(x2+pad+1)), min(image.height, int(y2+pad+1))))


@lru_cache(maxsize=1)
def index():
    exact, references = {}, []
    for record in RECORDS:
        with Image.open(ANNOTATIONS / record['original_image']) as opened:
            image = opened.convert('RGB')
        exact[pixels(image)] = (record, (0, 0), 'original')
        if record.get('crop_xyxy'):
            crop = record['crop_xyxy']
            exact[pixels(image.crop(crop))] = (record, tuple(crop[:2]), 'training_crop')
        for label in record['labels']:
            f = feature(context_crop(image, label['box_xyxy']))
            if f is not None:
                references.append((record, label, f))
    return exact, references


def public_case(record):
    return dict(image_id=record['image_id'], product_model=record['product_model'],
                annotation_status=record['annotation_status'], split=record.get('split'),
                label_names=list(dict.fromkeys(l['label_ko'] for l in record['labels'])),
                original_image='/annotations/' + record['original_image'],
                overlay_image='/annotations/' + record['overlay_image'],
                interpretation=record['interpretation'], factory_verified=False,
                required_evidence=record.get('required_evidence'))


def lookup(image, selected_product):
    matched = index()[0].get(pixels(image))
    if not matched:
        return None, None
    record, offset, variant = matched
    labels = []
    for label in record['labels']:
        item = dict(label)
        item['box_xyxy'] = [v-offset[i % 2] for i, v in enumerate(label['box_xyxy'])]
        item.update(interpretation_source='reviewed_source_annotation',
                    type_status='source_visual_label', cause=None)
        labels.append(item)
    rois = [[v-offset[i % 2] for i, v in enumerate(box)]
            for box in record.get('inspection_rois', [])]
    marked = image.copy()
    draw = ImageDraw.Draw(marked)
    for i, label in enumerate(labels):
        draw.rectangle(label['box_xyxy'], outline='#007b57', width=max(2, image.width//250))
        xy = label['box_xyxy']
        draw.text((xy[0], max(0, xy[1]-12)), f"LABEL {i+1}: {label['class_name']}", fill='#007b57')
    for roi in rois:
        draw.rectangle(roi, outline='#df8b00', width=max(2, image.width//250))
    result = public_case(record)
    result.update(match_method='identical_decoded_RGB_pixels', variant=variant,
                  labels=labels, inspection_rois=rois,
                  product_mismatch=record['product_model'] != selected_product,
                  provenance='원본 자료의 시각 검토 라벨입니다. 공장 최종 판정은 아직 없습니다.')
    return result, marked


def similar_cases(image, detections, selected_product, k=3):
    queries = [(i+1, feature(context_crop(image, b['box_xyxy'])))
               for i, b in enumerate(detections)]
    if not queries:
        queries = [(None, feature(image))]
    candidates = {}
    for record, label, ref in index()[1]:
        if record['product_model'] != selected_product:
            continue
        for region_number, query in queries:
            if query is None:
                continue
            score = float(np.dot(query, ref))
            key = record['image_id']
            if key not in candidates or score > candidates[key][0]:
                case = public_case(record)
                case.update(reference_label=label['label_ko'],
                            observation=label['observation'],
                            recommended_checks=label['recommended_checks'],
                            query_region_number=region_number,
                            evidence_role='visual_reference_only',
                            note='유사 외형 참고 사례이며 업로드 사진의 유형 판정이 아닙니다.')
                candidates[key] = (score, case)
    return [c[1] for c in sorted(candidates.values(), key=lambda x:x[0], reverse=True)[:k]]
