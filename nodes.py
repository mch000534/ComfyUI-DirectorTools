"""ComfyUI IMAGE adapter and bounded temporary source preview."""

import os
import math
import uuid

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

from .geometry import MAX_SIZE, MIN_ZOOM, MAX_ZOOM, RATIOS, camera_angles, crop_rect, validate_settings
from .refinement_prompt import refinement_prompt
from .shots import workflow_presets


def sample_crop(image, rect, width, height):
    """Sample output pixel centers, using row chunks to bound grid memory."""
    x, y, cw, ch = rect
    sh, sw = image.shape[1:3]
    source = image.detach().movedim(-1, 1).float()
    result = torch.empty((1, 3, height, width), device=image.device, dtype=torch.float32)
    xs = 2 * (x + (torch.arange(width, device=image.device, dtype=torch.float32) + .5) * cw / width) / sw - 1
    for start in range(0, height, 128):
        stop = min(height, start + 128)
        ys = 2 * (y + (torch.arange(start, stop, device=image.device, dtype=torch.float32) + .5) * ch / height) / sh - 1
        gy, gx = torch.meshgrid(ys, xs, indexing='ij')
        grid = torch.stack((gx, gy), dim=-1).unsqueeze(0)
        result[:, :, start:stop, :] = F.grid_sample(
            source, grid, mode='bilinear', padding_mode='border', align_corners=False)
    return result.movedim(1, -1).to(dtype=image.dtype).contiguous()


def sample_panorama(image, width, height, center_x, center_y, zoom, camera_height=0):
    """Perspective camera looking into an equirectangular texture with periodic U."""
    sh, sw = image.shape[1:3]
    yaw, pitch, tangent = camera_angles(center_x, center_y, zoom)
    sy, cy, sp, cp = math.sin(yaw), math.cos(yaw), math.sin(pitch), math.cos(pitch)
    source = image.detach().movedim(-1, 1).float()
    # One wrapped column at each side also interpolates across the texture seam.
    source = torch.cat((source[..., -1:], source, source[..., :1]), dim=-1)
    result = torch.empty((1, 3, height, width), device=image.device, dtype=torch.float32)
    xs = (2 * (torch.arange(width, device=image.device, dtype=torch.float32) + .5) / width - 1) * tangent * width / height
    for start in range(0, height, 128):
        stop = min(height, start + 128)
        ys = -(2 * (torch.arange(start, stop, device=image.device, dtype=torch.float32) + .5) / height - 1) * tangent
        y, x = torch.meshgrid(ys, xs, indexing='ij')
        py, pz = y * cp + sp, -y * sp + cp
        wx, wz = x * cy + pz * sy, -x * sy + pz * cy
        norm = torch.sqrt(x * x + y * y + 1)
        if camera_height:
            dx, dy, dz = wx / norm, py / norm, wz / norm
            distance = -camera_height * dy + torch.sqrt(1 - camera_height**2 + (camera_height * dy)**2)
            wx, py, wz = distance * dx, camera_height + distance * dy, distance * dz
            norm = 1.0
        u = torch.remainder(torch.atan2(wx, wz) / math.tau + .5, 1)
        v = .5 - torch.asin((py / norm).clamp(-1, 1)) / math.pi
        grid = torch.stack((2 * (u * sw + 1) / (sw + 2) - 1, 2 * v - 1), dim=-1).unsqueeze(0)
        result[:, :, start:stop, :] = F.grid_sample(source, grid, mode='bilinear',
                                                  padding_mode='border', align_corners=False)
    return result.movedim(1, -1).to(dtype=image.dtype).contiguous()


def source_preview(image):
    import folder_paths

    sh, sw = image.shape[1:3]
    scale = min(1, 1536 / max(sw, sh))
    preview_width, preview_height = max(1, round(sw * scale)), max(1, round(sh * scale))
    thumbnail = F.interpolate(image.detach().movedim(-1, 1).float(),
                              size=(preview_height, preview_width),
                              mode='bilinear', align_corners=False, antialias=True)
    pixels = thumbnail[0].movedim(0, -1).cpu().numpy()
    pixels = (np.clip(pixels, 0, 1) * 255).round().astype(np.uint8)
    filename = f'director_tools_panorama_{uuid.uuid4().hex}.png'
    Image.fromarray(pixels).save(os.path.join(folder_paths.get_temp_directory(), filename),
                                 compress_level=1)
    return {'filename': filename, 'subfolder': '', 'type': 'temp',
            'source_width': sw, 'source_height': sh}


class DirectorToolsPanoramaViewer:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': ('IMAGE', {'tooltip': 'One RGB image. 360 Panorama expects an equirectangular 2:1 panorama.'}),
            'aspect_ratio': ([*RATIOS, 'Free'], {'default': '16:9'}),
            'width': ('INT', {'default': 1920, 'min': 1, 'max': MAX_SIZE, 'step': 1}),
            'height': ('INT', {'default': 1080, 'min': 1, 'max': MAX_SIZE, 'step': 1}),
            'center_x': ('FLOAT', {'default': .5, 'min': 0, 'max': 1, 'step': .001,
                                   'round': False, 'tooltip': 'Normalized horizontal source center.'}),
            'center_y': ('FLOAT', {'default': .5, 'min': 0, 'max': 1, 'step': .001,
                                   'round': False, 'tooltip': 'Normalized vertical source center.'}),
            'zoom': ('FLOAT', {'default': 1.0, 'min': MIN_ZOOM, 'max': MAX_ZOOM, 'step': .01,
                               'round': False, 'tooltip': '360: 1 gives 75 degree vertical FOV. 360: 0.5 gives a wider view. Flat: values up to 1 fill viewport. Larger values zoom in.'}),
        }, 'optional': {
            'projection': (['360 Panorama', 'Flat'], {'default': '360 Panorama',
                           'tooltip': '360 wraps longitude and outputs perspective. Flat keeps legacy crop behavior.'}),
            'camera_height': ('FLOAT', {'default': 0.0, 'min': -0.8, 'max': 0.8, 'step': .01,
                              'round': False, 'display': 'slider',
                              'tooltip': 'Height in sphere radii. Positive moves up; 0 is sphere center. Simulated sphere movement, not real scene depth. Ignored in Flat mode.'}),
        }, 'hidden': {'extra_pnginfo':'EXTRA_PNGINFO','unique_id':'UNIQUE_ID'}}

    RETURN_TYPES = ('IMAGE','STRING','STRING')
    RETURN_NAMES = ('image','prompt','presets_json')
    FUNCTION = 'frame'
    CATEGORY = 'image/Director Tools'
    OUTPUT_NODE = True
    DESCRIPTION = 'Drag the image in a fixed viewport and scroll to zoom. Run once to load preview; run again to render changes. The prompt output guides image-to-image detail enhancement and distortion correction while preserving the scene.'

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # A temp PNG can disappear while tensor results remain in ComfyUI's cache.
        # Explicit runs must regenerate the preview. Upstream caches still apply.
        return float('nan')

    def frame(self, image, aspect_ratio, width, height, center_x, center_y, zoom, projection='Flat', camera_height=0.0,extra_pnginfo=None,unique_id=None):
        if isinstance(camera_height, bool) or not isinstance(camera_height, (int, float)) or not math.isfinite(camera_height) or not -.8 <= camera_height <= .8:
            raise ValueError('camera_height must be finite and between -0.8 and 0.8 sphere radii.')
        aspect = validate_settings(aspect_ratio, width, height, center_x, center_y, zoom)
        if projection not in ('Flat', '360 Panorama'):
            raise ValueError('Unknown projection. Select 360 Panorama or Flat.')
        if not isinstance(image, torch.Tensor) or image.ndim != 4 or image.shape[0] != 1:
            raise ValueError('Director Tools · Panorama viewer requires a single IMAGE with shape [1,H,W,3].')
        if image.shape[-1] != 3 or min(image.shape[1:3]) < 1 or not image.is_floating_point():
            raise ValueError('Director Tools · Panorama viewer requires a non-empty floating point RGB IMAGE.')
        presets_json=workflow_presets(extra_pnginfo,unique_id)
        rect = crop_rect(image.shape[2], image.shape[1], aspect, center_x, center_y, zoom)
        with torch.inference_mode():
            if projection == '360 Panorama':
                output = sample_panorama(image, width, height, center_x, center_y, zoom, camera_height)
            else:
                output = sample_crop(image, rect, width, height)
            preview = source_preview(image)
        return {'ui': {'director_tools_panorama': [preview]},
                'result': (output,refinement_prompt(projection,camera_height),presets_json)}
