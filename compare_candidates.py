"""Choose candidates by held-out photo validation, never the external challenge."""
import json,shutil
from pathlib import Path
from prepare_dataset import ROOT,sha

def main():
 candidates=[]
 for path in (ROOT/'evaluation/repaired/report.json',ROOT/'runs/repaired/train-3/evaluation/report.json'):
  if not path.exists():continue
  r=json.loads(path.read_text(encoding='utf-8'));v=r['summary']['val']
  # Define selection explicitly: held-out TP, then fewer FP, then train TP.
  key=(v['tp'],-v['fp'],r['summary']['train']['tp'])
  candidates.append((key,path,r))
 if not candidates:raise RuntimeError('No evaluated candidate available')
 _,path,r=max(candidates,key=lambda x:x[0])
 if 'runs' in path.parts:
  weights=path.parent.parent/'weights/best.pt'
  assert sha(weights)==r['model_sha256']
  shutil.copy2(weights,ROOT/'weights/defect_types.pt')
  shutil.copytree(path.parent,ROOT/'evaluation/repaired',dirs_exist_ok=True)
 (ROOT/'MODEL_EVALUATION.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'CANDIDATE_SELECTION.json').write_text(json.dumps(dict(rule='maximize held-out full-photo TP, then minimize FP, then maximize train TP; no external challenge used',selected_report=str(path.relative_to(ROOT)),candidates=[dict(report=str(p.relative_to(ROOT)),key=list(k),summary=x['summary']) for k,p,x in candidates]),ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(r['summary'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
