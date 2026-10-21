"""Image-only, conservative local reference matching. Not a trained YOLO model."""
from functools import lru_cache
import cv2
import numpy as np
from PIL import Image
from label_engine import RECORDS, ANNOTATIONS

def _descriptor(image):
    gray=cv2.cvtColor(np.asarray(image.convert('RGB')),cv2.COLOR_RGB2GRAY)
    gray=cv2.resize(gray,(128,128),interpolation=cv2.INTER_AREA)
    gray=cv2.equalizeHist(gray)
    # NumPy HOG keeps reference matching portable across OpenCV 4/5 builds,
    # including builds without the optional objdetect HOGDescriptor class.
    gx=cv2.Sobel(gray,cv2.CV_32F,1,0);gy=cv2.Sobel(gray,cv2.CV_32F,0,1)
    mag,angle=cv2.cartToPolar(gx,gy,angleInDegrees=True)
    bins=((angle%180)/20).astype(int)%9
    cells=np.zeros((8,8,9),dtype=np.float32)
    for y in range(8):
        for x in range(8):
            ys=slice(y*16,(y+1)*16);xs=slice(x*16,(x+1)*16)
            cells[y,x]=np.bincount(bins[ys,xs].ravel(),weights=mag[ys,xs].ravel(),minlength=9)
    blocks=[]
    for y in range(7):
        for x in range(7):
            block=cells[y:y+2,x:x+2].ravel()
            block=block/(np.linalg.norm(block)+1e-8)
            block=np.minimum(block,.2)
            blocks.append(block/(np.linalg.norm(block)+1e-8))
    h=np.concatenate(blocks)
    return h/(np.linalg.norm(h)+1e-8)

@lru_cache(maxsize=1)
def _catalog():
    data=[]
    for record in RECORDS:
        with Image.open(ANNOTATIONS/record['original_image']) as f: im=f.convert('RGB')
        data.append((record['product_model'],record['image_id'],_descriptor(im)))
    return data

def guess_product(image):
    """Model name suggestion only when close to a known visual reference."""
    feat=_descriptor(image)
    scores=sorted([(float(np.dot(feat,reference)),p,n) for p,n,reference in _catalog()],reverse=True)
    top=scores[0]
    different=max([s for s in scores if s[1]!=top[1]],default=(0,'', ''))
    acceptable=top[0]>=0.93 and top[0]-different[0]>=0.025
    return {'model':top[1] if acceptable else None,'similarity':round(top[0],3),
            'reference':top[2], 'status':'reference_match' if acceptable else 'not_identified',
            'method':'HOG appearance comparison (not a trained product classifier)'}
