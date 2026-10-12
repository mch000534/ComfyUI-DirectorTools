"""Image-to-image editing guidance; does not modify image pixels."""

def refinement_prompt(projection, camera_height=0):
    if projection == '360 Panorama':
        opening = ('Refine the supplied perspective image extracted from a 360-degree panorama. '
                   'Use it as a single camera view, not as an equirectangular image. ')
        correction = ('Correct residual spherical warping, curved architectural lines that should be straight, '
                      'and unnatural wide-angle stretching near the frame edges. ')
        if camera_height:
            correction += ('Reduce artificial warping from the simulated off-center panorama viewpoint '
                           'using only the visible scene; do not invent hidden surfaces. ')
    else:
        opening = 'Refine the supplied cropped image for image-to-image enhancement. '
        correction = ('Correct visible lens distortion and unnatural wide-angle stretching only where present. ')
    return (opening +
            'Preserve the original composition, framing, viewing direction, apparent field of view, '
            'subject identities, object positions, scene layout, lighting, colors and visual style. ' +
            correction +
            'Restore natural proportions and coherent geometry while preserving valid perspective convergence '
            'and intentionally curved objects. Do not force converging lines to become parallel. '
            'Improve clarity and fine detail, refine material textures, and reduce blur, noise, jagged edges '
            'and compression artifacts without oversharpening, halos, waxy surfaces or invented details. '
            'Keep the same aspect ratio and image boundaries. Do not crop, change the camera angle, '
            'redesign the scene, add or remove objects, or introduce text or watermarks. '
            'Output one refined image of the same scene.')
