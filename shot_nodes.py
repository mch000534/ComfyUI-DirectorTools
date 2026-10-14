"""Batch panorama renders and labeled contact sheets, using existing sampling."""
import json
import math
from pathlib import Path
import uuid

import numpy as np
from PIL import Image, ImageDraw
import torch
import torch.nn.functional as F

from .nodes import sample_panorama
from .shots import degree_framing, parse_presets

DEFAULT_PRESETS = json.dumps({'schema_version':1,'shots':[{
    'shot_id':'SH010','name':'Wide','source_id':'panorama_A','yaw':0,'pitch':0,
    'vertical_fov':75,'width':1920,'height':1080,'aspect_ratio':'16:9','camera_height':0
}]},indent=2)

def validate_image(image, single=False):
    if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[-1]!=3 or min(image.shape[:3])<1 or not image.is_floating_point():
        raise ValueError('Expected a nonempty floating point RGB IMAGE [batch,H,W,3].')
    if single and image.shape[0]!=1:
        raise ValueError('Batch Panorama requires one source panorama; shots share that source.')

def validate_sheet(columns, thumb_size, count):
    if type(columns) is not int or not 1<=columns<=8:
        raise ValueError('columns must be 1–8.')
    if type(thumb_size) is not int or not 64<=thumb_size<=512:
        raise ValueError('thumb_size must be 64–512.')
    if not 1<=count<=64:
        raise ValueError('Contact sheets accept 1–64 images.')

def contact_sheet(images, labels, columns, thumb_size):
    validate_sheet(columns,thumb_size,len(images))
    columns=min(columns,len(images))
    rows=math.ceil(len(images)/columns)
    band=24
    sizes=[]
    for image in images:
        h,w=image.shape[1:3]
        scale=min(thumb_size/w,thumb_size/h)
        sizes.append((max(1,round(w*scale)),max(1,round(h*scale))))
    cell_width=max(w for w,h in sizes)
    cell_height=max(h for w,h in sizes)
    # Fit cells to actual thumbnails, retaining aspect and a separate label band.
    # Sheet is a CPU float32 visualization. Original shot tensors stay untouched.
    canvas=Image.new('RGB',(columns*cell_width,rows*(cell_height+band)),(22,27,34))
    draw=ImageDraw.Draw(canvas)
    for i,(image,label) in enumerate(zip(images,labels)):
        tw,th=sizes[i]
        small=F.interpolate(image.detach().movedim(-1,1).float(),size=(th,tw),mode='bilinear',align_corners=False,antialias=True)
        pixels=(small[0].movedim(0,-1).clamp(0,1).cpu().numpy()*255).round().astype(np.uint8)
        x,y=(i%columns)*cell_width,(i//columns)*(cell_height+band)
        canvas.paste(Image.fromarray(pixels),(x+(cell_width-tw)//2,y+(cell_height-th)//2))
        # PIL's bundled font cannot render arbitrary glyphs on all hosts. IDs are ASCII;
        # names remain lossless in metadata. Sheet captions are intentionally short.
        caption=label.encode('ascii','replace').decode('ascii')[:max(6,cell_width//7)]
        draw.text((x+4,y+cell_height+5),caption,fill=(229,233,240))
    return torch.from_numpy(np.array(canvas).astype(np.float32)/255).unsqueeze(0)

class DirectorToolsBatchPanorama:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'presets_json':('STRING',{'multiline':True,'default':DEFAULT_PRESETS}),
            'columns':('INT',{'default':3,'min':1,'max':8}),
            'thumb_size':('INT',{'default':256,'min':64,'max':512,'tooltip':'Thumbnail longest edge. Cells follow image aspect ratio; labels have a separate 24 px band.'}),
            'save_files':('BOOLEAN',{'default':False,'tooltip':'Write unique shot PNG and JSON pairs in output/director_tools when explicitly run.'}),
        }}
    RETURN_TYPES=('IMAGE','IMAGE','STRING')
    RETURN_NAMES=('shot_images','contact_sheet','metadata_json')
    OUTPUT_IS_LIST=(False,False,False)
    OUTPUT_NODE=True
    FUNCTION='render'
    CATEGORY='image/Super Director Tools'
    DESCRIPTION='Render all named camera presets from one panorama. Shot images are one IMAGE batch; all presets must share width and height. Labels appear only on the contact sheet.'

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # An explicit save run creates a fresh package. Non-saving runs can be cached.
        return float('nan') if kwargs.get('save_files',False) else None

    def render(self,image,presets_json,columns,thumb_size,save_files):
        validate_image(image,single=True)
        if type(save_files) is not bool:
            raise ValueError('save_files must be boolean.')
        document=parse_presets(presets_json)
        shots=document['shots']
        validate_sheet(columns,thumb_size,len(shots))
        dimensions={(shot['width'],shot['height']) for shot in shots}
        if len(dimensions)!=1:
            raise ValueError('IMAGE batch requires all presets to have the same width and height. Set matching dimensions, or render different sizes in separate Batch Panorama nodes.')
        images=[]
        with torch.inference_mode():
            for shot in shots:
                cx,cy,zoom=degree_framing(shot['yaw'],shot['pitch'],shot['vertical_fov'])
                images.append(sample_panorama(image,shot['width'],shot['height'],cx,cy,zoom,shot['camera_height']))
            sheet=contact_sheet(images,[s['shot_id'] for s in shots],columns,thumb_size)
            batch=torch.cat(images,dim=0)
        metadata={**document,'source_size':[int(image.shape[2]),int(image.shape[1])],
                  'projection':'360 Panorama','fov_axis':'vertical'}
        if save_files:
            import folder_paths
            directory=Path(folder_paths.get_output_directory())/'director_tools'/uuid.uuid4().hex
            directory.mkdir(parents=True,exist_ok=False)
            for shot,output in zip(shots,images):
                filename=directory/('shot_'+shot['shot_id'])
                pixels=(output.detach()[0].float().clamp(0,1).cpu().numpy()*255).round().astype(np.uint8)
                Image.fromarray(pixels).save(filename.with_suffix('.png'))
                filename.with_suffix('.json').write_text(json.dumps({
                    'schema_version':1,'shot':shot,'source_size':metadata['source_size'],
                    'projection':'360 Panorama','fov_axis':'vertical',
                },ensure_ascii=False,indent=2),encoding='utf-8')
            (directory/'camera_presets.json').write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8')
            metadata['saved_subfolder']=f'director_tools/{directory.name}'
        return {'result':(batch,sheet,json.dumps(metadata,ensure_ascii=False,indent=2))}

def numbered_labels(prefix, start_number, count):
    if not isinstance(prefix,str) or len(prefix)>80 or any(ord(c)<32 or ord(c)==127 for c in prefix):
        raise ValueError('prefix must be a single line of at most 80 characters.')
    if type(start_number) is not int or not 0<=start_number<=999999999:
        raise ValueError('start_number must be an integer between 0 and 999999999.')
    return [f'{prefix}{start_number+i:03d}' for i in range(count)]


class DirectorToolsContactSheet:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'images':('IMAGE',),
            'columns':('INT',{'default':3,'min':1,'max':8}),
            'thumb_size':('INT',{'default':256,'min':64,'max':512,'tooltip':'Thumbnail longest edge. Cells follow image aspect ratio; labels have a separate 24 px band.'}),
            'prefix':('STRING',{'default':'SH','tooltip':'Label prefix, for example SH or Shot_. Leave blank for numbers only.'}),
            'start_number':('INT',{'default':1,'min':0,'max':999999999,'tooltip':'First image number. Sequential numbering, padded to at least three digits.'}),
        }}
    RETURN_TYPES=('IMAGE',)
    RETURN_NAMES=('contact_sheet',)
    FUNCTION='assemble'
    CATEGORY='image/Super Director Tools'
    DESCRIPTION='Create a contact sheet from an IMAGE batch with automatically numbered labels. Prefix SH and start_number 10 generate SH010, SH011… Originals are unchanged.'

    def assemble(self,images,columns,thumb_size,prefix='SH',start_number=1):
        validate_image(images)
        validate_sheet(columns,thumb_size,len(images))
        captions=numbered_labels(prefix,start_number,len(images))
        with torch.inference_mode():
            return (contact_sheet([images[i:i+1] for i in range(len(images))],captions,columns,thumb_size),)
