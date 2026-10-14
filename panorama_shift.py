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
    CATEGORY='image/Super Director Tools'
    DESCRIPTION=('Circularly shift a panorama horizontally without changing pixels or size. '
                 'Inspect the original left/right join at the center with shift_x=0.5. '
                 'The prompt guides interior seam repair while locking both outer edges and preserving equirectangular projection.')

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
            prompt=('The original join remains across the outer left and right edges of the image; '
                    'there is no interior seam to repair. Both edge regions are protected. '
                    'Do not regenerate, redraw, retouch or blend either edge or any other part of this image. '
                    'Return the supplied panorama unchanged. For a separate central seam-repair pass, '
                    'first use Panorama Shift with shift_x=0.5 on a panorama wider than one pixel '
                    'to move the original join into the middle of the image.')
            return shifted,prompt
        prompt=(
            'Perform a localized inpainting edit on the supplied horizontally shifted equirectangular '
            '360-degree panorama. Treat the supplied image as the fixed source canvas. '
            'HIGHEST PRIORITY: Lock the left and right regions, including both outer edge columns, '
            'exactly as supplied. Do not regenerate, redraw, retouch, relight, recolor, sharpen, denoise '
            'or blend these protected regions. Their existing wraparound connection must remain unchanged. ' +
            location +
            'Only regenerate the minimum interior strip needed to repair this seam; at the default '
            'half-width shift this is the middle of the image. Treat everything outside that strip as '
            'unmasked, read-only reference and copy it unchanged from the supplied image. '
            'Use the adjacent unchanged content as reference and locally redraw only mismatched regions '
            'inside the strip to align architectural lines, '
            'object contours, material textures and repeated patterns. Remove visible discontinuities, '
            'double edges, ghosting, stitching artifacts and abrupt changes in color, exposure or lighting. '
            'Make the transition spatially coherent and improve local clarity and detail without smearing '
            'the seam or blurring away the mismatch. Preserve the scene layout, object identities and '
            'positions, lighting direction, visual style and all unaffected regions. '
            'Keep the exact image dimensions, aspect ratio, current horizontal orientation and '
            'equirectangular projection, including its intentional stretching near the poles. '
            'Do not convert the panorama to a perspective or fisheye view, straighten the entire panorama, '
            'crop, resize, rotate, shift the image again, add or remove objects, or introduce text or watermarks. '
            'Match the repaired strip to the untouched content along both boundaries of the strip. '
            'Output the supplied full panorama with only the interior seam strip replaced, in the same '
            'shifted orientation. All pixels outside the repair strip, especially the left and right '
            'edge regions, must remain identical to the supplied image. Do not regenerate the full panorama.'
        )
        return shifted,prompt
