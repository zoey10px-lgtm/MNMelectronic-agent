"""Select the Vice single-class detector when installed; retain legacy fallback."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY_CLASSES = ['fracture', 'dent', 'porosity', 'missing_feature']
VICE_CLASSES = ['Defect1']

def verify_bundle():
    configured = os.environ.get('MM_MODEL_PATH', '').strip()
    path = Path(configured).expanduser() if configured else ROOT / 'weights' / 'exp-4.pt'
    if path.is_file():
        expected = os.environ.get('MM_MODEL_SHA256', '').strip().lower()
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected and checksum != expected:
            raise RuntimeError('Vice model SHA-256 does not match MM_MODEL_SHA256')
        return path, {'source': 'vice_exp4', 'class_names': VICE_CLASSES,
                      'model_sha256': checksum, 'assessment': 'evaluation_pending'}
    if configured:
        raise RuntimeError('MM_MODEL_PATH is set but the weight file does not exist: ' + str(path))
    legacy = ROOT / 'weights' / 'defect_types.pt'
    report_path = ROOT / 'MODEL_EVALUATION.json'
    if not legacy.is_file() or not report_path.is_file():
        raise RuntimeError('No usable YOLO weights were found.')
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if report.get('class_names') != LEGACY_CLASSES:
        raise RuntimeError('Legacy class mapping does not match the evaluation.')
    if hashlib.sha256(legacy.read_bytes()).hexdigest() != report.get('model_sha256'):
        raise RuntimeError('Legacy model and evaluation do not match.')
    return legacy, report
