"""Exercise the real upload/analysis/confirmation/media path using the installed model."""
import base64,io,json,os,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
 with tempfile.TemporaryDirectory() as tmp:
  os.environ['MM_DATA_DIR']=tmp
  import app as module
  from audit_dataset import audit
  audit()
  module.load_model()
  client=module.app.test_client()
  health=client.get('/health').get_json()
  assert health['evaluation']['status']=='limited_photo_holdout_only',health
  assert health['active_classes']==['fracture','dent','porosity','missing_feature']
  assert client.get('/').status_code==200
  results=[]
  # Source photo and JPEG derivative must BOTH use the real inference path.
  source=ROOT/'annotations/originals/A376_reference_02.png'
  images=[('registered_original',Image.open(source).convert('RGB')),
          ('external_housing',Image.open(ROOT/'evaluation/external_housing.png').convert('RGB'))]
  for name,im in images:
   raw=io.BytesIO();im.save(raw,format='JPEG',quality=85)
   data=dict(product='AUTO',message='',photos=[dict(name='renamed.jpg',url='data:image/jpeg;base64,'+base64.b64encode(raw.getvalue()).decode())])
   response=client.post('/api/analyze',json=data)
   assert response.status_code==201,response.get_json()
   d=response.get_json();vision=d['analysis']['vision'];photo=vision['images'][0]
   assert vision['class_names']==health['active_classes']
   assert photo['inference_status']=='complete'
   if name=='external_housing':
    from detector import iou
    assert any(b['label']=='fracture' and iou(b['box_xyxy'],[300,195,365,230])>=.5 for b in photo['detections']),photo['detections']
   assert photo['registered_label'] is None,'JPEG derivative must not inherit exact-source labels'
   assert client.get(photo['annotated_image']).status_code==200
   foreign=module.app.test_client();assert foreign.get(photo['annotated_image']).status_code==404
   assert client.post('/api/complaints/'+d['id']+'/confirm').status_code==200
   assert client.get('/api/complaints/'+d['id']+'/status').status_code==200
   results.append(dict(name=name,returned_count=photo['detection_count'],types=vision['predicted_types'],inference_complete=True,media_access=True,foreign_session_denied=True,confirmation=True))
  # Guard against treating stored source annotations as detector predictions.
  from unittest.mock import patch
  source_data=dict(product='AUTO',photos=[dict(name='source.png',url='data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode())])
  with patch.object(module,'inspect',side_effect=lambda im:([],im.copy(),[],['test_stub'])):
   check=client.post('/api/analyze',json=source_data).get_json()['analysis']['vision']
  assert check['images'][0]['registered_label']['labels']
  assert check['detection_count']==0 and check['predicted_types']==[]
  assert client.post('/api/analyze',json={'product':'AUTO','photos':[{'url':'not-an-image'}]}).status_code==400
  result=dict(status='passed',health=health,api_cases=results,invalid_image_rejected=True,source_labels_not_used_as_predictions=True)
  (ROOT/'PACKAGE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
