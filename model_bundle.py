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
        expected = os.environ.get('MM_MODEL_SHA256', 'd522fc938cd3478d1deafe536fc9d438f91a9b7024ddede307d7c78d7a4846c9').strip().lower()
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected and checksum != expected:
            raise RuntimeError('Vice model SHA-256 does not match MM_MODEL_SHA256')
        return path, {'source': 'vice_exp4', 'class_names': VICE_CLASSES,
                      'model_sha256': checksum, 'assessment': 'evaluation_pending'}
    raise RuntimeError('Vice exp-4.pt is required; legacy models are disabled. Check MM_MODEL_DOWNLOAD_URL and build logs.')
