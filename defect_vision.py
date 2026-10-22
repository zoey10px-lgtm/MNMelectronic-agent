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

def classify(images, findings, language='ko'):
    """Returns status and indexed findings, matching YOLO boxes; never overwrites YOLO results."""
    if not os.environ.get('OPENAI_API_KEY','').strip():
        return {'status':'not_configured','findings':[]}
    content=[]
    targets=[]
    for image_i, (image, result) in enumerate(zip(images,findings),1):
        for det_i, box in enumerate(result.get('detections',[])[:4],1):
            x1,y1,x2,y2=map(int,box['box_xyxy'])
            w,h=image.size
            pad=max(8,int(max(x2-x1,y2-y1)*0.2))
            crop=image.crop((max(0,x1-pad),max(0,y1-pad),min(w,x2+pad),min(h,y2+pad)))
            crop.thumbnail((640,640))
            b=io.BytesIO()
            crop.convert('RGB').save(b,format='JPEG',quality=78)
            content.append({'type':'input_text','text':f'Image {image_i}, detection {det_i}. The following is a crop of a YOLO-suspected region; do not assume it is defective.'})
            content.append({'type':'input_image','image_url':'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()})
            targets.append((image_i,det_i))
    if not targets:
        return {'status':'no_detections','findings':[]}
    try:
        model=os.environ.get('OPENAI_VISION_MODEL') or os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
        payload={'model':model,'store':False,'max_output_tokens':1200,
          'instructions':('Inspect ONLY the supplied cropped candidate images. Provide a tentative defect type for each. '
          'Some boxes may contain undamaged background or normal features: use category unclear in that case. '
          'Do not invent material specifications or claim a confirmed defect. '
          'Every finding must be tied to the exact image_number and detection_number supplied. '
          'Write descriptions in '+{'ko':'Korean','en':'English','vi':'Vietnamese'}.get(language,'Korean')+'.'),
          'input':[{'role':'user','content':content}],
          'text':{'format':{'type':'json_schema','name':'defect_crop_classification','strict':True,'schema':SCHEMA}}}
        r=requests.post('https://api.openai.com/v1/responses',json=payload,
          headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'].strip()},timeout=(10,65))
        if not r.ok:
            logging.warning('Crop classifier HTTP %s',r.status_code)
            return {'status':'api_error','findings':[]}
        raw=r.json()
        chunks=[p['text'] for item in raw.get('output',[]) if item.get('type')=='message'
            for p in item.get('content',[]) if p.get('type')=='output_text']
        parsed=json.loads(''.join(chunks))
        allowed=set(targets)
        results=[]
        for f in parsed.get('findings',[]):
            key=(f.get('image_number'),f.get('detection_number'))
            if key not in allowed or f.get('category') not in CATEGORIES:
                continue
            results.append({k:f[k] for k in ['image_number','detection_number','category','description','uncertainty']})
        return {'status':'complete' if results else 'unavailable','model':model,'source':'vision_llm_crop',
                'findings':results,'disclaimer':'AI visual hypotheses; require verification'}
    except (requests.RequestException,ValueError,KeyError,TypeError):
        logging.exception('Crop classification failed')
        return {'status':'unavailable','findings':[]}
