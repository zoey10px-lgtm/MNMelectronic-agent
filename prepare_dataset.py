"""Full-photo + context training views. Derivatives retain their source split."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
import yaml
ROOT=Path(__file__).resolve().parent
CLASSES=['fracture','dent','porosity','missing_feature']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def build():
 records=json.loads((ROOT/'annotations/records.json').read_text(encoding='utf-8'))['images']
 ds=ROOT/'training_dataset'
 if ds.exists():shutil.rmtree(ds)
 manifest=[]
 for split in ('train','val'):
  (ds/'images'/split).mkdir(parents=True);(ds/'labels'/split).mkdir(parents=True)
 for r in records:
  if r['annotation_status']!='typed_visual_label' or not r['labels']:continue
  split=r['split'];path=ROOT/'annotations'/r['original_image']
  with Image.open(path) as opened:im=opened.convert('RGB')
  w,h=im.size;views=[('full',(0,0,w,h))]
  if split=='train':
   boxes=[l['box_xyxy'] for l in r['labels']]
   x1=min(b[0] for b in boxes);y1=min(b[1] for b in boxes);x2=max(b[2] for b in boxes);y2=max(b[3] for b in boxes)
   for index,pad in enumerate((0.75,2.0)):
    span=max(x2-x1,y2-y1,48)
    crop=(max(0,int(x1-pad*span)),max(0,int(y1-pad*span)),min(w,int(x2+pad*span)),min(h,int(y2+pad*span)))
    if crop not in [v[1] for v in views]:views.append((f'context{index}',crop))
  for role,crop in views:
   l,t,rr,b=crop;cw,ch=rr-l,b-t;name=r['image_id']+'__'+role
   dest=ds/'images'/split/(name+'.jpg');im.crop(crop).save(dest,quality=95);lines=[]
   for label in r['labels']:
    a,c,d,e=label['box_xyxy'];a-=l;d-=l;c-=t;e-=t
    assert 0<=a<d<=cw and 0<=c<e<=ch,(r['image_id'],crop,label)
    lines.append(f'{CLASSES.index(label["class_name"])} {(a+d)/2/cw:.8f} {(c+e)/2/ch:.8f} {(d-a)/cw:.8f} {(e-c)/ch:.8f}')
   lp=ds/'labels'/split/(name+'.txt');lp.write_text('\n'.join(lines)+'\n',encoding='utf-8')
   manifest.append(dict(file=dest.relative_to(ds).as_posix(),source_id=r['image_id'],source_sha256=sha(path),split=split,role=role,crop=list(crop),image_sha256=sha(dest),label_sha256=sha(lp),classes=[l['class_name'] for l in r['labels']]))
 train={m['source_sha256'] for m in manifest if m['split']=='train'};val={m['source_sha256'] for m in manifest if m['split']=='val'}
 assert not train&val,'Source leakage'
 (ds/'data.yaml').write_text(yaml.safe_dump(dict(path=ds.as_posix(),train='images/train',val='images/val',names=dict(enumerate(CLASSES))),sort_keys=False),encoding='utf-8')
 result=dict(unique_train_sources=len(train),unique_val_sources=len(val),views=manifest,normal_part_images=0,specimen_independence='unknown',excluded_unreviewed_sources=[r['image_id'] for r in records if r['annotation_status']!='typed_visual_label'])
 (ds/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result
if __name__=='__main__':
 m=build();print(json.dumps({k:v for k,v in m.items() if k!='views'},ensure_ascii=False,indent=2))
