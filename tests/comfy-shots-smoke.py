"""Real execution test: use an isolated ComfyUI instance, never a production queue."""
import io
import json
import os
from pathlib import Path
import time
import urllib.request
from urllib.parse import urlencode
from PIL import Image

base=os.environ.get('COMFY_TEST_URL','http://127.0.0.1:8199').rstrip('/')
root=Path(__file__).resolve().parents[1]
def request(path,data=None):
    req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)

info=request('/object_info')
assert info['DirectorToolsBatchPanorama']['output_is_list']==[False,False,False]
assert info['DirectorToolsContactSheet']['output']==['IMAGE']
payload=json.loads((root/'example_workflows/director_tools_batch_api.json').read_text())
payload['prompt']['2']['inputs']['save_files']=True
payload['prompt']['5']={'class_type':'DirectorToolsContactSheet','inputs':{'images':['2',0],'columns':3,'thumb_size':64,'prefix':'SH','start_number':10}}
payload['prompt']['6']={'class_type':'SaveImage','inputs':{'images':['5',0],'filename_prefix':'DirectorTools/batch_consumer'}}
prompt_id=request('/prompt',payload)['prompt_id']
deadline=time.monotonic()+30
while time.monotonic()<deadline:
    history=request('/history/'+prompt_id).get(prompt_id)
    if history:break
    time.sleep(.1)
else:raise AssertionError('Execution timed out')
assert history['status']['status_str']=='success',history['status']
outputs=history['outputs']['3']['images']
assert len(outputs)==3,outputs
for ref,expected in zip(outputs,[(640,360)]*3):
    with urllib.request.urlopen(base+'/view?'+urlencode(ref)) as response:
        with Image.open(io.BytesIO(response.read())) as image:assert image.size==expected,image.size
sheet=history['outputs']['4']['images'][0]
with urllib.request.urlopen(base+'/view?'+urlencode(sheet)) as response:
    with Image.open(io.BytesIO(response.read())) as image:assert image.size==(768,168),image.size
consumed=history['outputs']['6']['images']
assert len(consumed)==1,consumed
with urllib.request.urlopen(base+'/view?'+urlencode(consumed[0])) as response:
    with Image.open(io.BytesIO(response.read())) as image:assert image.size==(192,60),image.size
if os.environ.get('COMFY_TEST_OUTPUT'):
    files=list((Path(os.environ['COMFY_TEST_OUTPUT'])/'director_tools').rglob('shot_*.png'))
    assert len(files)==3,files
    for file in files:
        data=json.loads(file.with_suffix('.json').read_text())
        with Image.open(file) as image:assert image.size==(data['shot']['width'],data['shot']['height'])
print('ComfyUI: node registration, true uniform-size IMAGE batch, three Save Image outputs, contact sheet and sidecars passed.')
