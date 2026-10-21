"""Check the dataset's source counts, class coverage, boxes and split isolation."""
import json
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image
from prepare_dataset import ROOT,CLASSES,sha

def audit():
 records=json.loads((ROOT/'annotations/records.json').read_text(encoding='utf-8'))['images']
 errors=[];counts={};hashes={};byproduct=defaultdict(Counter)
 for split in ('train','val'):
  selected=[r for r in records if r.get('split')==split and r.get('training_included')]
  counts[split]=dict(unique_photos=len(selected),boxes_by_class=dict(Counter(l['class_name'] for r in selected for l in r['labels'])))
  hashes[split]=set()
  for r in selected:
   path=ROOT/'annotations'/r['original_image'];hashes[split].add(sha(path))
   with Image.open(path) as im:
    if im.size!=(r['width'],r['height']):errors.append(r['image_id']+': dimension mismatch')
    for l in r['labels']:
     a,b,c,d=l['box_xyxy']
     if not (0<=a<c<=im.width and 0<=b<d<=im.height):errors.append(r['image_id']+': invalid box')
     if l['class_name'] not in CLASSES or CLASSES[l['class_id']]!=l['class_name']:errors.append(r['image_id']+': class mismatch')
     byproduct[r['product_model']][l['class_name']]+=1
  if counts[split]['unique_photos']==0:errors.append('empty '+split)
 if hashes['train']&hashes['val']:errors.append('source image leaked across train/val')
 result=dict(original_photos=len(records),counts=counts,product_class_counts={k:dict(v) for k,v in byproduct.items()},errors=errors,normal_part_photos=0,unsupported_requested_types=['scratch','assembly_gap'],specimen_independence='unknown',source_split_overlap=len(hashes['train']&hashes['val']),
  findings=['The old 98 training images derive from only 14 unique source photos.',
  'The old training and validation inputs are tight defect crops; the web app accepts full photos.',
  'Only one porosity training source exists; offline brightness transforms add no new physical examples.',
  'Historical input contained a single-class checkpoint. The current checkpoint includes weights/defect_types.pt and its hash-bound four-class MODEL_EVALUATION.json.',
  'All labeled A376 photos show fracture; class and product appearance are confounded.',
  'The former registered-image display prioritized stored labels, which does not measure model prediction accuracy.',
  'No scratch or assembly-gap labels exist in the supplied data.'])
 (ROOT/'DATA_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 assert not errors,errors
 return result
if __name__=='__main__':print(json.dumps(audit(),ensure_ascii=False,indent=2))
