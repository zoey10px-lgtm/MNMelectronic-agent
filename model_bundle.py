"""Require the verified Vice YOLO26x single-class checkpoint only."""
import hashlib
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
VICE_CLASSES = ['Defect1']
VICE_SHA256 = 'd522fc938cd3478d1deafe536fc9d438f91a9b7024ddede307d7c78d7a4846c9'
def verify_bundle():
    configured = os.environ.get('MM_MODEL_PATH', '').strip()
    path = Path(configured).expanduser() if configured else ROOT / 'weights' / 'exp-4.pt'
    if not path.is_file():
        raise RuntimeError('Vice exp-4.pt not found. Check MM_MODEL_DOWNLOAD_URL.')
    expected = os.environ.get('MM_MODEL_SHA256', VICE_SHA256).strip().lower()
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError('Vice exp-4.pt SHA-256 mismatch.')
    return path, {'source':'vice_exp4', 'class_names':VICE_CLASSES,
                  'model_sha256':actual, 'assessment':'evaluation_pending'}
