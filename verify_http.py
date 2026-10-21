"""Start real Waitress and upload a JPEG through HTTP, with cookie ownership."""
import base64,io,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from PIL import Image
import requests
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
 env=dict(os.environ,MM_DATA_DIR=temp,PORT='18080',MM_OPEN_BROWSER='0',HOST='0.0.0.0')
 proc=subprocess.Popen([sys.executable,str(ROOT/'serve.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 try:
  s=requests.Session();url='http://127.0.0.1:18080'
  for _ in range(100):
   try:
    response=s.get(url+'/health',timeout=1)
    if response.status_code==200:break
   except requests.ConnectionError:pass
   if proc.poll() is not None:raise RuntimeError(proc.stderr.read().decode())
   time.sleep(.1)
  else:raise RuntimeError('HTTP server startup timed out')
  im=Image.open(ROOT/'evaluation/external_housing.png').convert('RGB');b=io.BytesIO();im.save(b,format='JPEG',quality=85)
  response=s.post(url+'/api/analyze',json=dict(product='AUTO',message='',photos=[dict(name='fresh-upload.jpg',url='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode())]),timeout=60)
  assert response.status_code==201,response.text
  data=response.json();photo=data['analysis']['vision']['images'][0]
  from detector import iou
  assert any(b['label']=='fracture' and iou(b['box_xyxy'],[300,195,365,230])>=.5 for b in photo['detections']),photo
  assert s.get(url+photo['annotated_image'],timeout=3).status_code==200
  assert requests.get(url+photo['annotated_image'],timeout=3).status_code==404
  assert s.post(url+'/api/complaints/'+data['id']+'/confirm',timeout=3).status_code==200
  result=dict(status='passed',server='Waitress',entrypoint='python serve.py',bind_host='0.0.0.0',port_environment_respected=True,http_status=response.status_code,product_mode='AUTO',image_encoding='JPEG85',detections=photo['detections'],registered_label_used=False,media_owner_access=True,foreign_session_denied=True,complaint_confirmation=True)
  (ROOT/'HTTP_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps(result,ensure_ascii=False,indent=2))
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
