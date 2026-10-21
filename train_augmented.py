"""Fine-tune on the supplied 164 offline-augmented training images.

Holdout originals are copied unchanged from reviewed source annotations.
Inference and evaluation keep the previous detector and 0.25 threshold.
"""
import argparse,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def prepare():
 import hashlib,shutil
 import yaml
 from PIL import Image
 ds=ROOT/'training_dataset'
 manifest=json.loads((ds/'manifest.json').read_text(encoding='utf-8'))
 records=json.loads((ROOT/'annotations/records.json').read_text(encoding='utf-8'))['images']
 train_sources={m['source_image_id'] for m in manifest}
 val_sources={r['image_id'] for r in records if r.get('split')=='val' and r['labels']}
 assert not train_sources&val_sources
 assert len(manifest)==164 and len(train_sources)==14
 for m in manifest:
  image=ds/'images/train'/m['image_file'];label=ds/'labels/train'/(image.stem+'.txt')
  assert image.is_file() and label.is_file()
  with Image.open(image) as im:w,h=im.size
  for row in label.read_text().splitlines():
   cls,x,y,bw,bh=map(float,row.split())
   assert int(cls)==cls and int(cls) in range(4) and bw>0 and bh>0
   assert -1e-7<=x-bw/2<x+bw/2<=1+1e-7 and -1e-7<=y-bh/2<y+bh/2<=1+1e-7
 for kind in ('images','labels'):(ds/kind/'val').mkdir(parents=True,exist_ok=True)
 for r in records:
  if r['image_id'] not in val_sources:continue
  source=ROOT/'annotations'/r['original_image'];dest=ds/'images/val'/source.name
  shutil.copy2(source,dest)
  assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(dest.read_bytes()).digest()
  w,h=r['width'],r['height'];lines=[]
  for a in r['labels']:
   x1,y1,x2,y2=a['box_xyxy'];lines.append(f"{a['class_id']} {(x1+x2)/2/w:.8f} {(y1+y2)/2/h:.8f} {(x2-x1)/w:.8f} {(y2-y1)/h:.8f}")
  (ds/'labels/val'/(source.stem+'.txt')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
 cfg=dict(path=ds.as_posix(),train='images/train',val='images/val',names={0:'fracture',1:'dent',2:'porosity',3:'missing_feature'})
 for name in ('data.yaml','dataset.yaml'):(ds/name).write_text(yaml.safe_dump(cfg,sort_keys=False),encoding='utf-8')
 return ds/'data.yaml'

def main():
 p=argparse.ArgumentParser();p.add_argument('--epochs',type=int,default=40);p.add_argument('--batch',type=int,default=8);p.add_argument('--device',default='auto');p.add_argument('--source',default=str(ROOT/'weights/previous_model.pt'));p.add_argument('--lr0',type=float,default=.0001);args=p.parse_args()
 import torch
 from ultralytics import YOLO
 import ultralytics.utils.torch_utils as tu
 tu.NUM_THREADS=min(8,max(1,(os.cpu_count() or 1)-1));torch.set_num_threads(tu.NUM_THREADS)
 data=prepare();device=('0' if torch.cuda.is_available() else 'cpu') if args.device=='auto' else args.device
 model=YOLO(args.source)
 print('TRAINING_INPUT: 164 images, 14 unique originals, 186 boxes; VAL: 4 unchanged held-out originals',flush=True)
 print('SOURCE:',args.source,flush=True)
 results=model.train(data=str(data),epochs=args.epochs,imgsz=640,batch=args.batch,nbs=args.batch,device=device,
  project=str(ROOT/'runs/augmented'),name='train',exist_ok=False,workers=0,cache='disk',
  optimizer='AdamW',lr0=args.lr0,lrf=.1,weight_decay=.0005,warmup_epochs=1,
  patience=12,seed=42,deterministic=True,cls_pw=.5,cls=1.0,
  degrees=0,translate=0,scale=0,fliplr=0,flipud=0,shear=0,perspective=0,
  mosaic=0,mixup=0,copy_paste=0,hsv_h=0,hsv_s=0,hsv_v=0,
  plots=True,amp=False)
 best=Path(results.save_dir)/'weights/best.pt';assert best.is_file()
 from evaluate_model import evaluate,quality_key,validation_signature
 candidate_dir=ROOT/'evaluation/augmented_retraining'
 report=evaluate(best,candidate_dir)
 report.update(training_data=dict(images=164,unique_originals=14,boxes=186,validation_originals=4),training_run=str(Path(results.save_dir).relative_to(ROOT)))
 (ROOT/'AUGMENTED_MODEL_EVALUATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 import shutil
 shutil.copy2(best,ROOT/'weights/augmented_candidate.pt')
 old=json.loads((ROOT/'PRE_RETRAINING_EVALUATION.json').read_text(encoding='utf-8'))
 assert validation_signature(old)==validation_signature(report)
 improved=quality_key(report)>quality_key(old)
 comparison=dict(improved_on_same_validation=improved,selection_rule='more validation TP, then fewer validation FP, then more training TP',previous=old['summary'],retrained=report['summary'],previous_key=quality_key(old),retrained_key=quality_key(report),previous_external=old['challenges'][0]['typed'],retrained_external=report['challenges'][0]['typed'],candidate_weights='weights/augmented_candidate.pt',candidate_sha256=report['model_sha256'],active_model='retrained' if improved else 'previous_retained')
 if improved:
  shutil.copy2(best,ROOT/'weights/defect_types.pt')
  (ROOT/'MODEL_EVALUATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  shutil.copytree(candidate_dir,ROOT/'evaluation/repaired',dirs_exist_ok=True)
 (ROOT/'RETRAINING_COMPARISON.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
 print('FINAL_COMPARISON:',json.dumps(comparison,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
