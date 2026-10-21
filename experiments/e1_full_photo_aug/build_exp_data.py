"""Full-photo originals (14 train / 4 val) from records.json -> YOLO dirs. No derived images."""
import json, shutil
from pathlib import Path
R=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent/'data_orig'
recs=json.load(open(R/'annotations/records.json'))['images']
names={0:'fracture',1:'dent',2:'porosity',3:'missing_feature'}
for sp in ('train','val'):
    (out/'images'/sp).mkdir(parents=True,exist_ok=True); (out/'labels'/sp).mkdir(parents=True,exist_ok=True)
n={'train':0,'val':0}
for r in recs:
    if r['annotation_status']!='typed_visual_label': continue
    sp=r['split']; src=R/'annotations'/r['original_image']
    shutil.copy2(src,out/'images'/sp/src.name)
    w,h=r['width'],r['height']; L=[]
    for a in r['labels']:
        x1,y1,x2,y2=a['box_xyxy']; L.append(f"{a['class_id']} {(x1+x2)/2/w:.8f} {(y1+y2)/2/h:.8f} {(x2-x1)/w:.8f} {(y2-y1)/h:.8f}")
    (out/'labels'/sp/(src.stem+'.txt')).write_text('\n'.join(L)+'\n'); n[sp]+=1
import yaml
(out/'data.yaml').write_text(yaml.safe_dump(dict(path=str(out.resolve()),train='images/train',val='images/val',names=names),sort_keys=False))
print(n)
