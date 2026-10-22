"""Classify only YOLO-cropped suspect regions with a vision-capable LLM.

Visual labels are independent AI hypotheses, NOT verified inspection decisions.
"""
import base64
import io
import json
import logging
import os
import requests

CATEGORIES = ['scratch','dent','fracture','porosity','missing_feature','assembly_gap','deformation','burr','corrosion','coating_peel','contamination','other','unclear']
SCHEMA = {'type':'object','additionalProperties':False,
 'properties':{'findings':{'type':'array','items':{'type':'object','additionalProperties':False,
   'properties':{'image_number':{'type':'integer'},'detection_number':{'type':'integer'},
    'category':{'type':'string','enum':CATEGORIES},'description':{'type':'string'},
    'uncertainty':{'type':'string'}},
   'required':['image_number','detection_number','category','description','uncertainty']}}},
 'required':['findings']}


def _image_part(image, max_side=1280):
    picture=image.convert('RGB').copy()
    picture.thumbnail((max_side,max_side))
    stream=io.BytesIO()
    picture.save(stream,format='JPEG',quality=92,optimize=True)
    return {'type':'input_image','image_url':'data:image/jpeg;base64,'+
            base64.b64encode(stream.getvalue()).decode('ascii')}

def _window(image, box, scale, min_side):
    w,h=image.size
    x1,y1,x2,y2=map(float,box)
    cx,cy=(x1+x2)/2,(y1+y2)/2
    side=max(min_side,max(x2-x1,y2-y1)*scale)
    left=max(0,int(cx-side/2));top=max(0,int(cy-side/2))
    right=min(w,int(cx+side/2));bottom=min(h,int(cy+side/2))
    return image.crop((left,top,max(left+1,right),max(top+1,bottom)))

def _request(model, content, language, token_count=1200):
    payload={'model':model,'store':False,'max_output_tokens':token_count,
     'instructions':('You are inspecting a suspected electronics component defect. '
       'For each numbered region compare the close view with its wider context. '
       'Identify a tentative defect category, not a confirmed quality decision. Use precise taxonomy: missing_feature = metal chipped away, broken off, absent material or jagged notch; fracture = visible crack or split with material largely present; deformation = bent or warped metal without evident missing material; dent = localized depression; scratch = linear surface abrasion; burr = protruding extra metal. When both distortion and material loss occur, choose missing_feature as primary. Distinguish actual geometry from reflections. '
       'Ordinary surfaces and shadows may be false positive YOLO boxes; choose unclear if evidence is insufficient. '
       'Use the exact image_number and detection_number supplied. '
       'For each classification, state the visible distinguishing evidence, avoid unsupported certainty. Descriptions must be in '+{'ko':'Korean','en':'English','vi':'Vietnamese'}.get(language,'Korean')+'.'),
     'input':[{'role':'user','content':content}],
     'text':{'format':{'type':'json_schema','name':'defect_crop_classification','strict':True,'schema':SCHEMA}}}
    response=requests.post('https://api.openai.com/v1/responses',json=payload,
      headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'].strip()},
      timeout=(10,70))
    if not response.ok:
        logging.warning('Vision classification HTTP %s', response.status_code)
        return []
    raw=response.json()
    chunks=[part['text'] for item in raw.get('output',[]) if item.get('type')=='message'
             for part in item.get('content',[]) if part.get('type')=='output_text']
    return json.loads(''.join(chunks)).get('findings',[])

def classify(images, findings, language='ko'):
    """YOLO coordinates are unchanged. Vision classifications remain tentative."""
    if not os.environ.get('OPENAI_API_KEY','').strip():
        return {'status':'not_configured','findings':[]}
    model=os.environ.get('OPENAI_VISION_MODEL') or os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
    content=[]; targets=set()
    for image_i,(image,info) in enumerate(zip(images,findings),1):
        for det_i,box in enumerate(info.get('detections',[])[:4],1):
            coords=box['box_xyxy']
            content.append({'type':'input_text','text':f'Image {image_i}, detection {det_i}: close-up of the detected box and a wider view of the SAME area.'})
            content.append(_image_part(_window(image,coords,2.5,160),1024))
            content.append(_image_part(_window(image,coords,5.0,420),1280))
            targets.add((image_i,det_i))
    if not targets:
        return {'status':'no_detections','findings':[]}
    try:
        first=_request(model,content,language)
        result={(v.get('image_number'),v.get('detection_number')):v for v in first
                if (v.get('image_number'),v.get('detection_number')) in targets and v.get('category') in CATEGORIES}
        unclear=[key for key in targets if key not in result or result[key]['category']=='unclear']
        if unclear:
            # The original image is supplied only for uncertain detections.
            retry=[]
            for i,j in sorted(unclear):
                original=images[i-1]
                box=findings[i-1]['detections'][j-1]['box_xyxy']
                retry.append({'type':'input_text','text':f'Image {i}, detection {j}: entire source photo followed by wider candidate region. Use the region coordinates as a hint, not as proof of damage.'})
                retry.append(_image_part(original,1280))
                retry.append(_image_part(_window(original,box,6.0,500),1280))
            for v in _request(model,retry,language,max(700,350*len(unclear))):
                key=(v.get('image_number'),v.get('detection_number'))
                if key in unclear and v.get('category') in CATEGORIES:
                    if key not in result or (result[key]['category']=='unclear' and v['category']!='unclear'):
                        result[key]=v
        ordered=[{k:result[key][k] for k in ['image_number','detection_number','category','description','uncertainty']}
                 for key in sorted(result) if all(k in result[key] for k in ['description','uncertainty'])]
        return {'status':'complete' if ordered else 'unavailable','model':model,
                'source':'vision_llm_multiscale','findings':ordered,
                'disclaimer':'AI visual hypotheses; human verification required'}
    except (requests.RequestException,ValueError,KeyError,TypeError,IndexError):
        logging.exception('Multiscale defect classification failed')
        return {'status':'unavailable','findings':[]}
