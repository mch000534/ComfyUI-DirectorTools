"""Validated portable camera presets. Degree contract mirrored in presets.mjs."""
import json
import math
import re
from .geometry import BASE_FOV, MIN_ZOOM, MAX_ZOOM, camera_angles, validate_settings

MIN_FOV = math.degrees(2*math.atan(math.tan(math.radians(BASE_FOV/2))/MAX_ZOOM))
MAX_FOV = math.degrees(2*math.atan(math.tan(math.radians(BASE_FOV/2))/MIN_ZOOM))
MAX_BATCH_PIXELS = 33554432

def workflow_presets(extra_pnginfo, unique_id):
    """Read only this viewer's saved presets from ComfyUI workflow metadata."""
    empty={'schema_version':1,'shots':[]}
    document=empty
    if isinstance(extra_pnginfo,dict) and unique_id is not None:
        workflow=extra_pnginfo.get('workflow')
        nodes=workflow.get('nodes',[]) if isinstance(workflow,dict) else []
        if isinstance(nodes,list):
            for node in nodes:
                if not isinstance(node,dict) or str(node.get('id'))!=str(unique_id):
                    continue
                properties=node.get('properties')
                if isinstance(properties,dict) and 'director_tools_shots' in properties:
                    saved=properties['director_tools_shots']
                    is_empty=isinstance(saved,dict) and type(saved.get('schema_version')) is int and saved==empty
                    document=empty if is_empty else parse_presets(json.dumps(saved,ensure_ascii=False))
                break
    return json.dumps(document,ensure_ascii=False,indent=2)

def framing_degrees(center_x, center_y, zoom):
    yaw,pitch,tangent = camera_angles(center_x,center_y,zoom)
    return dict(yaw=math.degrees(yaw),pitch=math.degrees(pitch),vertical_fov=math.degrees(2*math.atan(tangent)))

def degree_framing(yaw, pitch, vertical_fov):
    for name,value,low,high in [('yaw',yaw,-180,180),('pitch',pitch,-89.9,89.9),('vertical_fov',vertical_fov,MIN_FOV-1e-9,MAX_FOV+1e-9)]:
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low<=value<=high:
            raise ValueError(f'{name} must be finite and between {low:.3f} and {high:.3f}.')
    return (yaw/360+.5)%1, .5-pitch/180, min(MAX_ZOOM,max(MIN_ZOOM,math.tan(math.radians(BASE_FOV/2))/math.tan(math.radians(vertical_fov/2))))

def parse_presets(text):
    if not isinstance(text,str) or len(text)>262144:
        raise ValueError('Preset JSON must be at most 256 KiB.')
    try:
        doc = json.loads(text)
    except (ValueError,RecursionError) as error:
        raise ValueError('Invalid preset JSON.') from error
    if not isinstance(doc,dict) or type(doc.get('schema_version')) is not int or doc['schema_version']!=1 or not isinstance(doc.get('shots'),list) or not 1<=len(doc['shots'])<=64:
        raise ValueError('Expected schema_version 1 and 1–64 shots.')
    ids,sources,shots = set(),set(),[]
    pixels=0
    keys=['shot_id','name','source_id','yaw','pitch','vertical_fov','width','height','aspect_ratio','camera_height']
    for shot in doc['shots']:
        if not isinstance(shot,dict) or any(k not in shot for k in keys):
            raise ValueError('Shot is missing required fields.')
        for key in ['shot_id','name','source_id']:
            v=shot[key]
            if not isinstance(v,str) or not v.strip() or len(v)>80 or re.search(r'[\x00-\x1f\x7f]',v):
                raise ValueError(f'{key} must be 1–80 characters.')
        if not re.fullmatch(r'[A-Za-z0-9_-]+',shot['shot_id']) or shot['shot_id'].lower() in ids:
            raise ValueError('Shot IDs must be unique letters, numbers, underscores or hyphens.')
        ids.add(shot['shot_id'].lower()); sources.add(shot['source_id'])
        cx,cy,zoom=degree_framing(shot['yaw'],shot['pitch'],shot['vertical_fov'])
        if not isinstance(shot['aspect_ratio'],str):
            raise ValueError('Unknown aspect ratio.')
        validate_settings(shot['aspect_ratio'],shot['width'],shot['height'],cx,cy,zoom)
        h=shot['camera_height']
        if isinstance(h,bool) or not isinstance(h,(int,float)) or not math.isfinite(h) or not -.8<=h<=.8:
            raise ValueError('Camera height must be -0.8–0.8.')
        pixels+=shot['width']*shot['height']
        shots.append({k:shot[k] for k in keys})
    if len(sources)!=1:
        raise ValueError('Use one source_id per panorama document.')
    if pixels>MAX_BATCH_PIXELS:
        raise ValueError('Batch exceeds 32 megapixels; split the shot list.')
    return dict(schema_version=1,shots=shots)
