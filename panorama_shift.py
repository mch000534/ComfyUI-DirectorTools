"""Pixel-preserving circular panorama shift and localized seam-repair guidance."""
import math
import torch


class DirectorToolsPanoramaShift:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',{'tooltip':'Equirectangular panorama, usually 2:1. Supports IMAGE batches.'}),
            'shift_x':('FLOAT',{'default':0.5,'min':-1.0,'max':1.0,'step':0.001,
                              'tooltip':'Fraction of image width. Positive moves right, negative left. 0.5 moves the original left/right join to the middle. Circular, rounded to whole pixels.'}),
        }}

    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('image','prompt')
    FUNCTION='shift'
    CATEGORY='image/Director Tools'
    DESCRIPTION=('Circularly shift a panorama horizontally without changing pixels or size. '
                 'Inspect the original left/right join at the center with shift_x=0.5. '
                 'The prompt guides local image-to-image seam repair while preserving equirectangular projection.')

    def shift(self,image,shift_x=0.5):
        if isinstance(shift_x,bool) or not isinstance(shift_x,(int,float)) or not math.isfinite(shift_x) or not -1<=shift_x<=1:
            raise ValueError('shift_x must be finite and between -1 and 1 (fraction of image width).')
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or min(image.shape[:3])<1 or image.shape[-1] not in (1,3,4) or not image.is_floating_point():
            raise ValueError('Expected a nonempty floating point IMAGE [batch,H,W,channels], with 1, 3 or 4 channels.')
        width=image.shape[2]
        magnitude=math.floor(abs(shift_x)*width+0.5)
        shift_px=magnitude if shift_x>=0 else -magnitude
        seam_x=shift_px%width
        shifted=torch.roll(image,shifts=shift_px,dims=2)
        if seam_x:
            location=(f'The input panorama\'s original left/right join is now the vertical boundary '
                      f'at x={seam_x} pixels from the left ({100*seam_x/width:.2f}% of image width), '
                      f'between columns {seam_x-1} and {seam_x} using zero-based pixel coordinates. '
                      'Repair only a narrow vertical neighborhood around this boundary. ')
        else:
            location=('The original join remains across the outer left and right edges of the image. '
                      'Repair these two edge neighborhoods together as one continuous wraparound join. ')
        prompt=(
            'Repair the seam in the supplied horizontally shifted equirectangular 360-degree panorama. ' +
            location +
            'Inspect both sides and locally redraw only mismatched regions to align architectural lines, '
            'object contours, material textures and repeated patterns. Remove visible discontinuities, '
            'double edges, ghosting, stitching artifacts and abrupt changes in color, exposure or lighting. '
            'Make the transition spatially coherent and improve local clarity and detail without smearing '
            'the seam or blurring away the mismatch. Preserve the scene layout, object identities and '
            'positions, lighting direction, visual style and all unaffected regions. '
            'Keep the exact image dimensions, aspect ratio, current horizontal orientation and '
            'equirectangular projection, including its intentional stretching near the poles. '
            'Do not convert the panorama to a perspective or fisheye view, straighten the entire panorama, '
            'crop, resize, rotate, shift the image again, add or remove objects, or introduce text or watermarks. '
            'Keep the outer left and right edges mutually consistent for seamless horizontal wraparound. '
            'Output one repaired full panorama in the same shifted orientation.'
        )
        return shifted,prompt
