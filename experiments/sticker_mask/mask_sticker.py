import cv2, json, numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
recs=[r for r in json.load(open(R/'annotations/records.json'))['images'] if r['annotation_status']=='typed_visual_label']
out=HERE/'imgs'; out.mkdir(exist_ok=True)
def sticker_circle(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    m=(((hsv[...,0]<10)|(hsv[...,0]>168))&(hsv[...,1]>130)&(hsv[...,2]>90)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: return None
    i=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    if st[i,cv2.CC_STAT_AREA]<400: return None
    pts=cv2.findNonZero((lab==i).astype(np.uint8))
    (cx,cy),r=cv2.minEnclosingCircle(pts)
    return cx,cy,r*1.55
rows=[]
for r in recs:
    p=R/'annotations'/r['original_image']; img=cv2.imread(str(p)); h,w=img.shape[:2]
    c=sticker_circle(img); m=img.copy(); ov=0.0
    if c:
        cx,cy,rad=c; cv2.circle(m,(int(cx),int(cy)),int(rad),(114,114,114),-1)
        yy,xx=np.ogrid[:h,:w]; disc=(xx-cx)**2+(yy-cy)**2<=rad**2
        # overlap of disc with GT boxes (fraction of box area covered)
        for a in r['labels']:
            x1,y1,x2,y2=map(int,a['box_xyxy']); box=disc[y1:y2,x1:x2]; ov=max(ov,float(box.mean()) if box.size else 0)
    cv2.imwrite(str(out/(r['image_id']+'.png')),m)
    rows.append((r['image_id'],r['split'],bool(c),round(ov,2)))
for x in rows: print(x)
json.dump(rows,open(HERE/'mask_report.json','w'))
