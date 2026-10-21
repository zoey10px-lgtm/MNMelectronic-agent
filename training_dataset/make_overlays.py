import json, sys, cv2, numpy as np
from pathlib import Path
out=Path(sys.argv[1]); names={0:'fracture',1:'dent',2:'porosity',3:'missing_feature'}
col={0:(0,0,255),1:(0,200,0),2:(255,128,0),3:(255,0,255)}
coco=json.loads((out/'annotations_coco.json').read_text())
by={}
for a in coco['annotations']: by.setdefault(a['image_id'],[]).append(a)
errs=0
def draw(im):
    img=cv2.imread(str(out/im['file_name'])); h,w=img.shape[:2]
    assert (w,h)==(im['width'],im['height']),im['file_name']
    for a in by[im['id']]:
        x,y,bw,bh=a['bbox']
        if x<-1e-6 or y<-1e-6 or x+bw>w+1e-6 or y+bh>h+1e-6 or bw<=0 or bh<=0: raise SystemExit('bad box '+im['file_name'])
        cv2.rectangle(img,(int(x),int(y)),(int(x+bw),int(y+bh)),col[a['category_id']],2)
        cv2.putText(img,names[a['category_id']],(int(x),max(12,int(y)-4)),cv2.FONT_HERSHEY_SIMPLEX,0.45,col[a['category_id']],1,cv2.LINE_AA)
    return img
# YOLO file consistency check
for im in coco['images']:
    lines=(out/'labels/train'/(Path(im['file_name']).stem+'.txt')).read_text().split('\n'); lines=[l for l in lines if l]
    assert len(lines)==len(by[im['id']]),im['file_name']
    for l in lines:
        c,cx,cy,bw,bh=l.split(); assert all(0<=float(v)<=1 for v in (cx,cy,bw,bh))
print('YOLO/COCO consistent, all boxes inside image')
def sheet(ims,path,cell=300,cols=4):
    tiles=[]
    for im in ims:
        d=draw(im); h,w=d.shape[:2]; s=cell/max(h,w); d=cv2.resize(d,(int(w*s),int(h*s)))
        t=np.full((cell,cell,3),40,np.uint8); t[:d.shape[0],:d.shape[1]]=d
        cv2.putText(t,Path(im['file_name']).stem[-22:],(4,cell-6),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,255),1,cv2.LINE_AA)
        tiles.append(t)
    while len(tiles)%cols: tiles.append(np.full((cell,cell,3),40,np.uint8))
    rows=[np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]
    cv2.imwrite(str(path),np.vstack(rows))
srcs=sorted({i['source_image_id'] for i in coco['images']})
# one sheet per 2 sources: original + 3 derivatives each
sel=[]
for s in srcs:
    g=[i for i in coco['images'] if i['source_image_id']==s]
    sel+= g[:4]
for n in range(0,len(sel),16): sheet(sel[n:n+16],out/'overlays'/f'overlay_sheet_{n//16+1}.jpg')
print(sorted(p.name for p in (out/'overlays').iterdir()))
