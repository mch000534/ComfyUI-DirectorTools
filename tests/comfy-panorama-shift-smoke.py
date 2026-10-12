"""Run on an isolated ComfyUI host with the included test panorama in input."""
import io
import json
import math
import os
from pathlib import Path
import time
from urllib.parse import urlencode
import urllib.request
import numpy as np
from PIL import Image

base=os.environ.get('COMFY_TEST_URL','http://127.0.0.1:8199').rstrip('/')
root=Path(__file__).resolve().parents[1]
def request(path,data=None):
    req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)

info=request('/object_info/DirectorToolsPanoramaShift')['DirectorToolsPanoramaShift']
assert info['output']==['IMAGE','STRING']
assert info['output_name']==['image','prompt']
assert info['input']['required']['shift_x'][1]['default']==.5
payload=json.loads((root/'example_workflows/director_tools_panorama_shift_api.json').read_text())
with Image.open(root/'example_workflows/test-panorama.png') as source:original=np.array(source.convert('RGB'))
for shift in [.5,-.25,1]:
    payload['prompt']['2']['inputs']['shift_x']=shift
    response=request('/prompt',payload)
    assert not response.get('node_errors'),response
    prompt_id=response['prompt_id']
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        history=request('/history/'+prompt_id).get(prompt_id)
        if history:break
        time.sleep(.1)
    else:raise AssertionError('Execution timed out')
    assert history['status']['status_str']=='success',history['status']
    output=history['outputs']['3']['images'][0]
    with urllib.request.urlopen(base+'/view?'+urlencode(output)) as response:
        with Image.open(io.BytesIO(response.read())) as image:actual=np.array(image.convert('RGB'))
    pixels=math.floor(abs(shift)*original.shape[1]+.5)*(1 if shift>=0 else -1)
    np.testing.assert_array_equal(actual,np.roll(original,pixels,axis=1))
    text=history['outputs']['4']['text'][0]
    assert 'equirectangular' in text and 'stitching artifacts' in text
    seam=pixels%original.shape[1]
    assert (f'x={seam} pixels' if seam else 'outer left and right edges') in text,text
    print(f'Panorama Shift passed: shift_x={shift}, exact PNG pixels and STRING seam location.')
