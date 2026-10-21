import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from PIL import Image
from ultralytics import YOLO
import ultralytics.utils.torch_utils as tu
tu.NUM_THREADS=1
import torch; torch.set_num_threads(1)
from detector import detect, iou
R=ROOT; recs={r['image_id']:r for r in json.load(open(ROOT/'annotations/records.json'))['images'] if r['annotation_status']=='typed_visual_label'}
rep=json.load(open(HERE/'mask_report.json'))
keep=[(i,sp) for i,sp,ok,ov in rep if ov<=0.1]
def score(model,img,gt):
    pred,_,_,_=detect(model,img); used=set(); tp=loc=0
    for p in pred:
        best=max(((iou(p['box_xyxy'],t['box_xyxy']),k) for k,t in enumerate(gt) if k not in used),default=(0,None))
        if best[0]>=.5:
            loc+=1
            if p['label']==gt[best[1]]['class_name']: tp+=1; used.add(best[1])
    return tp,loc,len(pred),len(gt)
for name,w in (('current_app_model',ROOT/'weights/defect_types.pt'),('E1_generic_aug',ROOT/'runs/experiments/E1_orig14_aug100/weights/last.pt')):
    if not w.is_file():
        print('SKIPPED missing optional experiment:', name); continue
    m=YOLO(w); tot={'orig':[0,0,0,0],'masked':[0,0,0,0]}; per=[]
    for i,sp in keep:
        gt=recs[i]['labels']; row=[i,sp]
        for tag,path in (('orig',R/'annotations'/recs[i]['original_image']),('masked',HERE/'imgs'/(i+'.png'))):
            s=score(m,Image.open(path).convert('RGB'),gt); row.append((tag,)+s)
            for k in range(4): tot[tag][k]+=s[k]
        per.append(row)
    print('=====',name,'| photos',len(keep))
    for r in per: print(r)
    print('TOTAL (typedTP, locTP, npred, ngt):',tot)
