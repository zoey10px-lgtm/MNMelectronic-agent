"""Ensure inference uses the exact four-class model that was evaluated."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CLASSES=['fracture','dent','porosity','missing_feature']
def verify_bundle():
 path=ROOT/'weights'/'defect_types.pt';report_path=ROOT/'MODEL_EVALUATION.json'
 if not path.is_file() or not report_path.is_file():
  raise RuntimeError('Evaluated four-class model missing. Extract the complete revised ZIP, or run TRAIN_4CLASS.')
 report=json.loads(report_path.read_text(encoding='utf-8'))
 if report.get('class_names')!=CLASSES:raise RuntimeError('Evaluation class mapping is incompatible.')
 if hashlib.sha256(path.read_bytes()).hexdigest()!=report.get('model_sha256'):
  raise RuntimeError('Model and evaluation do not match. Re-evaluate the replacement model before use.')
 return path,report
