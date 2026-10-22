"""The single inference path used by the app and independent evaluation."""
from PIL import Image, ImageDraw
from interpretation import describe_detection
CONFIDENCE=0.25
CANDIDATE_CONFIDENCE=0.05

def iou(a,b):
 x1=max(a[0],b[0]);y1=max(a[1],b[1]);x2=min(a[2],b[2]);y2=min(a[3],b[3])
 inter=max(0,x2-x1)*max(0,y2-y1)
 return inter/(max(0,a[2]-a[0])*max(0,a[3]-a[1])+max(0,b[2]-b[0])*max(0,b[3]-b[1])-inter+1e-9)

def detect(model,image):
 raw=[];modes=[];w,h=image.size
 views=[('full_640',image,(0,0),640)]
 # The large one-class Vice model uses a single CPU inference pass to avoid
 # excessive latency and memory usage on small Render instances.
 is_vice = set(model.names.values()) == {'Defect1'}
 if is_vice:
  views=[('full_640',image,(0,0),640)]
 for angle,transpose in (() if is_vice else ((90,Image.Transpose.ROTATE_90),(180,Image.Transpose.ROTATE_180),(270,Image.Transpose.ROTATE_270))):
  views.append((f'rotation_{angle}',image.transpose(transpose),(0,0),640))
 # Always use the same search plan in evaluation and serving.
 if not is_vice and max(w,h)>800:views.append(('full_960',image,(0,0),960))
 if not is_vice and min(w,h)>=256:
  tw,th=round(w*.65),round(h*.65)
  for x,y in ((0,0),(w-tw,0),(0,h-th),(w-tw,h-th)):
   views.append(('tile_640',image.crop((x,y,x+tw,y+th)),(x,y),640))
 for mode,pic,(dx,dy),size in views:
  result=model.predict(pic,conf=CANDIDATE_CONFIDENCE,iou=0.5,imgsz=size,device='cpu',verbose=False)[0]
  modes.append(mode)
  for box in result.boxes:
   a,b,c,d=map(float,box.xyxy[0].tolist())
   if mode=='rotation_90':a,b,c,d=w-d,a,w-b,c
   elif mode=='rotation_180':a,b,c,d=w-c,h-d,w-a,h-b
   elif mode=='rotation_270':a,b,c,d=b,h-c,d,h-a
   coords=[max(0,a+dx),max(0,b+dy),min(w,c+dx),min(h,d+dy)]
   if coords[2]<=coords[0] or coords[3]<=coords[1]:continue
   raw.append(dict(label=model.names[int(box.cls[0])],confidence=float(box.conf[0]),box_xyxy=coords,search_mode=mode))
 raw.sort(key=lambda b:b['confidence'],reverse=True);merged=[]
 for box in raw:
  # Class-agnostic merging: contradictory types at the same location do not
  # become multiple alleged defects. Highest confidence wins.
  if any(iou(box['box_xyxy'],b['box_xyxy'])>.35 for b in merged):continue
  merged.append(box)
 confirmed=[describe_detection(b,w,h) for b in merged if b['confidence']>=CONFIDENCE][:10]
 weak=[describe_detection(b,w,h) for b in merged if b['confidence']<CONFIDENCE][:5]
 marked=image.copy();draw=ImageDraw.Draw(marked)
 for box in confirmed:
  xy=box['box_xyxy'];draw.rectangle(xy,outline='#ff2255',width=max(2,round(w/350)))
  x=max(0,min(xy[0],max(0,w-180)));y=max(0,xy[1]-16)
  draw.rectangle((x,y,min(w,x+180),y+16),fill='white')
  draw.text((x+2,y),f"{box['label']} {box['confidence']:.2f}",fill='#b50035')
 return confirmed,marked,weak,modes
