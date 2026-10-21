"""Verify rotated detections land on the original photo, independently of YOLO."""
from types import SimpleNamespace
import numpy as np
from PIL import Image,ImageDraw
from detector import detect
from evaluate_model import match
class ColorModel:
 names={0:'fracture'}
 def predict(self,pic,**kwargs):
  a=np.asarray(pic);ys,xs=np.where((a[:,:,0]>200)&(a[:,:,1]<30)&(a[:,:,2]<30))
  boxes=[]
  if len(xs):boxes=[SimpleNamespace(xyxy=np.array([[xs.min(),ys.min(),xs.max()+1,ys.max()+1]],dtype=float),cls=np.array([0]),conf=np.array([.95]))]
  return [SimpleNamespace(boxes=boxes)]
def main():
 im=Image.new('RGB',(200,140),'white');ImageDraw.Draw(im).rectangle((37,19,83,61),fill='red')
 pred,_,_,modes=detect(ColorModel(),im)
 assert len(pred)==1,pred
 assert pred[0]['box_xyxy']==[37,19,84,62],pred
 assert modes==['full_640','rotation_90','rotation_180','rotation_270']
 truth=[dict(class_name='dent',box_xyxy=[37,19,84,62])]
 assert match(pred,truth,typed=True)==dict(tp=0,fp=1,fn=1)
 assert match(pred,truth,typed=False)==dict(tp=1,fp=0,fn=0)
 print('rotation coordinates, duplicate merging, and class-aware evaluation passed')
if __name__=='__main__':main()
