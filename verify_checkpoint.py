"""Check a complete, portable checkpoint without modifying its data or model."""
import hashlib
import json
from pathlib import Path

from PIL import Image

from model_bundle import verify_bundle

ROOT = Path(__file__).resolve().parent


def verify():
    model, evaluation = verify_bundle()
    records = json.loads((ROOT / 'annotations/records.json').read_text(encoding='utf-8'))['images']
    assert len(records) == 31
    for record in records:
        path = ROOT / 'annotations' / record['original_image']
        with Image.open(path) as image:
            assert image.size == (record['width'], record['height']), path
            image.verify()
    ds = ROOT / 'training_dataset'
    manifest = json.loads((ds / 'manifest.json').read_text(encoding='utf-8'))
    train_sources = {m['source_image_id'] for m in manifest}
    val_records = [r for r in records if r.get('split') == 'val' and r['labels']]
    assert not train_sources & {r['image_id'] for r in val_records}
    assert len(manifest) == 164 and len(train_sources) == 14
    assert len([p for p in (ds / 'images/train').iterdir()
                if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]) == 164
    assert len(list((ds / 'labels/train').glob('*.txt'))) == 164
    boxes = 0
    for row in manifest:
        path = ds / 'images/train' / row['image_file']
        with Image.open(path) as image:
            image.verify()
        labels = (ds / 'labels/train' / (path.stem + '.txt')).read_text().splitlines()
        assert len(labels) == row['n_boxes']
        for label in labels:
            cls, x, y, width, height = map(float, label.split())
            assert int(cls) == cls and 0 <= cls < 4
            assert width > 0 and height > 0
            assert -1e-6 <= x-width/2 < x+width/2 <= 1+1e-6
            assert -1e-6 <= y-height/2 < y+height/2 <= 1+1e-6
            boxes += 1
    assert boxes == 186
    for record in val_records:
        source = ROOT / 'annotations' / record['original_image']
        dest = ds / 'images/val' / source.name
        assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(dest.read_bytes()).digest()
        expected = []
        for label in record['labels']:
            x1, y1, x2, y2 = label['box_xyxy']
            expected.append([label['class_id'], (x1+x2)/2/record['width'],
                             (y1+y2)/2/record['height'], (x2-x1)/record['width'],
                             (y2-y1)/record['height']])
        actual = [[float(v) for v in line.split()] for line in
                  (ds / 'labels/val' / (source.stem+'.txt')).read_text().splitlines()]
        assert len(actual) == len(expected)
        assert all(abs(a-b) < 1e-7 for aa, ee in zip(actual, expected) for a, b in zip(aa, ee))
    for path in ('templates/index.html', 'rag/documents.jsonl', 'rag/index_manifest.json',
                 'sample_photos/fracture.jpg', 'sample_photos/dent.jpg',
                 'sample_photos/porosity.jpg', 'sample_photos/missing_feature.jpg'):
        assert (ROOT/path).is_file(), path
    return dict(status='passed', original_photos=len(records), train_images=len(manifest),
                unique_train_sources=len(train_sources), train_boxes=boxes,
                unchanged_validation_originals=len(val_records),
                model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                stored_validation=evaluation.get('summary', {}).get('val'),
                model_source=evaluation.get('source', 'legacy'),
                model_evaluation_hash_matches=(evaluation.get('source') != 'vice_exp4'))


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
