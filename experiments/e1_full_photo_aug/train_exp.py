import sys, json, time, os
from pathlib import Path
import torch
from ultralytics import YOLO
import ultralytics.utils.torch_utils as tu
tu.NUM_THREADS=1; torch.set_num_threads(1)
ROOT=Path(__file__).resolve().parents[2]
name, data, epochs = sys.argv[1], sys.argv[2], int(sys.argv[3])
if not Path(data).is_absolute(): data=str(ROOT/data)
aug = sys.argv[4] if len(sys.argv)>4 else 'on'
P=dict(data=data,epochs=epochs,imgsz=640,batch=8,nbs=8,device='cpu',project=str(ROOT/'runs/experiments'),name=name,exist_ok=True,
       workers=0,optimizer='AdamW',lr0=1e-3,lrf=0.05,weight_decay=5e-4,warmup_epochs=2,patience=0,seed=0,deterministic=True,
       plots=False,amp=False,val=False,save_period=-1)
if aug=='on':
    P.update(mosaic=1.0,close_mosaic=max(1,epochs//6),mixup=0.0,degrees=15,translate=0.15,scale=0.5,fliplr=0.5,flipud=0.5,
             hsv_h=0.015,hsv_s=0.5,hsv_v=0.35,erasing=0.0)
else:
    P.update(mosaic=0,mixup=0,degrees=0,translate=0,scale=0,fliplr=0,flipud=0,hsv_h=0,hsv_s=0,hsv_v=0)
t=time.time()
m=YOLO(str(ROOT/'weights/pretrained_base.pt'))
print('classes in base:',len(m.names),flush=True)
m.train(**P)
print('DONE',name,round(time.time()-t),'s',flush=True)
