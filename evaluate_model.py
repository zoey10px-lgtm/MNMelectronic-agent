"""Evaluate real inference without lookup labels; install with a hash-bound report.

Validation sources are excluded from training. Four photos do not establish
universal defect recognition. External challenge is evaluation only.
"""
import argparse,hashlib,io,json,shutil,os
from pathlib import Path
from PIL import Image,ImageEnhance
from prepare_dataset import ROOT,CLASSES,sha
from detector import detect,iou,CONFIDENCE

def match(pred,truth,typed=True):
 used=set();tp=0
 for p in pred:
  scores=[(iou(p['box_xyxy'],t['box_xyxy']),i) for i,t in enumerate(truth) if i not in used and (not typed or p['label']==t['class_name'])]
  if scores:
   s,i=max(scores)
   if s>=0.5:tp+=1;used.add(i)
 return dict(tp=tp,fp=len(pred)-tp,fn=len(truth)-tp)

def evaluate(model_path,output):
 import torch
 from ultralytics import YOLO
 import ultralytics.utils.torch_utils as tu
 tu.NUM_THREADS=1
 torch.set_num_threads(1)
 model=YOLO(str(model_path));out=Path(output);out.mkdir(parents=True,exist_ok=True)
 rows=[];records=json.loads((ROOT/'annotations/records.json').read_text(encoding='utf-8'))['images']
 typed=set(model.names.values())==set(CLASSES)
 for r in records:
  if r['annotation_status']!='typed_visual_label':continue
  with Image.open(ROOT/'annotations'/r['original_image']) as f:im=f.convert('RGB')
  variants=[('full',im)]
  if r['split']=='val':
   b=io.BytesIO();im.save(b,format='JPEG',quality=85);b.seek(0)
   variants+=[('jpeg85',Image.open(b).convert('RGB')),('brightness',ImageEnhance.Brightness(im).enhance(.8))]
  for variant,pic in variants:
   pred,marked,weak,modes=detect(model,pic)
   marked.save(out/(r['image_id']+'__'+variant+'.jpg'),quality=90)
   rows.append(dict(source_id=r['image_id'],source_sha256=sha(ROOT/'annotations'/r['original_image']),split=r['split'],variant=variant,ground_truth=r['labels'],predictions=pred,candidates=weak,localization=match(pred,r['labels'],False),typed=match(pred,r['labels'],True)))
 summary={}
 for split in ('train','val'):
  selected=[r for r in rows if r['split']==split and r['variant']=='full']
  totals={k:sum(r['typed' if typed else 'localization'][k] for r in selected) for k in ('tp','fp','fn')}
  totals.update(images=len(selected),matched_images=sum(r['typed' if typed else 'localization']['tp']>0 for r in selected))
  totals['precision']=totals['tp']/max(1,totals['tp']+totals['fp']);totals['recall']=totals['tp']/max(1,totals['tp']+totals['fn']);summary[split]=totals
 summary['val_per_class']={c:{'gt':sum(t['class_name']==c for r in rows if r['split']=='val' and r['variant']=='full' for t in r['ground_truth']), 'tp':sum(match([p for p in r['predictions'] if p['label']==c],[t for t in r['ground_truth'] if t['class_name']==c])['tp'] for r in rows if r['split']=='val' and r['variant']=='full')} for c in CLASSES}
 # Fixed before training; enables comparing old and repaired detector fairly.
 external=ROOT/'evaluation'/'external_housing.png'
 challenges=[]
 if external.exists():
  im=Image.open(external).convert('RGB');pred,marked,weak,modes=detect(model,im);marked.save(out/'external_housing.jpg')
  truth=[dict(class_name='fracture',box_xyxy=[300,195,365,230])]
  challenges.append(dict(name='external_housing_screenshot_crop',training_used=False,annotation='manual_visual_evaluation_only',ground_truth=truth,predictions=pred,candidates=weak,localization=match(pred,truth,False),typed=match(pred,truth)))
 for color in ('white','black',(30,110,75)):
  im=Image.new('RGB',(640,480),color);pred,_,_,_=detect(model,im)
  challenges.append(dict(name='blank_'+str(color),training_used=False,predictions=pred,expected_count=0))
 report=dict(model_sha256=sha(model_path),class_names=list(model.names.values()),confidence_threshold=CONFIDENCE,iou_match_threshold=.5,summary=summary,cases=rows,challenges=challenges,
  assessment='limited_photo_holdout_only',specimen_independence='unknown',normal_part_images=0,
  unsupported_types=['scratch','assembly_gap'],universal_generalization_verified=False)
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return report

def quality_key(report):
 v=report['summary']['val'];t=report['summary']['train']
 return (v['tp'],-v['fp'],t['tp'])

def validation_signature(report):
 rows=[(c['source_sha256'],[(t['class_name'],t['box_xyxy']) for t in c['ground_truth']]) for c in report['cases'] if c['split']=='val' and c['variant']=='full']
 return json.dumps(rows,sort_keys=True)

def evaluate_and_install(path):
 candidate_dir=ROOT/'evaluation'/('candidate_'+sha(path)[:12])
 report=evaluate(path,candidate_dir)
 assert report['class_names']==CLASSES
 current=ROOT/'MODEL_EVALUATION.json'
 if current.is_file():
  old=json.loads(current.read_text(encoding='utf-8'))
  if validation_signature(old)==validation_signature(report) and quality_key(report)<quality_key(old):
   print('Candidate is worse on the same validation sources; retained the previously evaluated model.',flush=True)
   report['activation']='not_activated_previous_model_retained'
   return report
 target=ROOT/'weights'/'defect_types.pt';shutil.copy2(path,target)
 shutil.copytree(candidate_dir,ROOT/'evaluation'/'repaired',dirs_exist_ok=True)
 current.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('weights');p.add_argument('--out',default=str(ROOT/'evaluation'/'baseline'));args=p.parse_args()
 r=evaluate(args.weights,args.out);print(json.dumps(r['summary'],ensure_ascii=False,indent=2))
