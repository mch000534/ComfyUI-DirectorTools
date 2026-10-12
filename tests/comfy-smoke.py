"""Run against an isolated ComfyUI server with this node installed (default :8199)."""
import io
import json
import os
from pathlib import Path
import time
import urllib.request

from PIL import Image

base = os.environ.get('COMFY_TEST_URL', 'http://127.0.0.1:8199').rstrip('/')
root = Path(__file__).resolve().parents[1]


def request(path, data=None):
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(base + path, data=payload,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


info = request('/object_info/DirectorToolsPanoramaViewer')['DirectorToolsPanoramaViewer']
assert info['output'] == ['IMAGE','STRING','STRING']
assert info['output_name'] == ['image','prompt','presets_json']
assert info['output_node'] is True
extensions = request('/extensions')
assert any(path.endswith('/ComfyUI-DirectorTools/director_tools_panorama.js') for path in extensions), extensions
assert not any('/ComfyUI-DirectorTools/lib/' in path for path in extensions)
payload = json.loads((root / 'example_workflows/director_tools_panorama_api.json').read_text())
payload['prompt']['4']={'class_type':'PreviewAny','inputs':{'source':['2',1]}}
previous_source = None
for ratio, width, height, cx, zoom, h in [('16:9',1920,1080,.5,1,0),('Free',777,301,.75,2.7,.8),('9:16',608,1080,.15,1.3,-.8),('9:16',608,1080,.15,1.3,-.8)]:
    if previous_source and ratio == '9:16' and os.environ.get('COMFY_TEST_TEMP'):
        (Path(os.environ['COMFY_TEST_TEMP']) / previous_source['filename']).unlink(missing_ok=True)
    payload['prompt']['2']['inputs'].update(aspect_ratio=ratio, width=width, height=height, center_x=cx, zoom=zoom,camera_height=h)
    result = request('/prompt', payload)
    assert not result.get('node_errors'), result
    prompt_id = result['prompt_id']
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        history = request('/history/' + prompt_id).get(prompt_id)
        if history:
            break
        time.sleep(.1)
    else:
        raise AssertionError('Execution timed out')
    assert history['status']['status_str'] == 'success', history['status']
    prompt=history['outputs']['4']['text'][0]
    assert 'spherical' in prompt and 'perspective convergence' in prompt
    output = history['outputs']['3']['images'][0]
    from urllib.parse import urlencode
    with urllib.request.urlopen(base + '/view?' + urlencode(output)) as response:
        with Image.open(io.BytesIO(response.read())) as image:
            assert image.size == (width, height), image.size
    source = history['outputs']['2']['director_tools_panorama'][0]
    assert (source['source_width'], source['source_height']) == (2000,1000)
    assert source['type'] == 'temp'
    if previous_source:
        assert source['filename'] != previous_source['filename'], 'Explicit run reused a possibly expired temp preview.'
    previous_source = source
    print(f'ComfyUI execution passed: {ratio} {width}x{height}, center_x={cx}, zoom={zoom}, height={h}')
print('Registration, extension entry point, four real prompt executions, PNG dimensions and regenerated preview metadata passed.')
