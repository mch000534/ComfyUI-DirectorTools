"""Camera geometry; mirrored by web/lib/geometry.mjs."""

import math

RATIOS = {'16:9': 16 / 9, '9:16': 9 / 16, '1:1': 1.0,
          '4:3': 4 / 3, '3:2': 3 / 2, '2.39:1': 2.39}
MAX_SIZE = 8192
MIN_ZOOM = 0.5
MAX_ZOOM = 32.0
BASE_FOV = 75.0
PITCH_LIMIT = math.radians(89.9)


def validate_settings(aspect_ratio, width, height, center_x, center_y, zoom):
    if aspect_ratio not in (*RATIOS, 'Free'):
        raise ValueError('Unknown aspect ratio.')
    for name, value in [('width', width), ('height', height)]:
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= MAX_SIZE:
            raise ValueError(f'{name} must be an integer between 1 and {MAX_SIZE}.')
    for name, value, low, high in [('center_x', center_x, 0, 1), ('center_y', center_y, 0, 1),
                                  ('zoom', zoom, MIN_ZOOM, MAX_ZOOM)]:
        if not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{name} must be finite and between {low} and {high}.')
    if aspect_ratio != 'Free':
        ratio = RATIOS[aspect_ratio]
        if abs(width - height * ratio) > max(1, ratio) / 2 + 1e-7:
            raise ValueError('Output dimensions do not match the locked aspect ratio. '
                             'Adjust width/height or select Free.')
    # Use actual pixel dimensions; integer rounding must not stretch the crop.
    return width / height


def crop_rect(source_width, source_height, aspect, center_x, center_y, zoom):
    """Return floating point (left, top, width, height) in source edge coordinates."""
    width = min(source_width, source_height * aspect) / max(1, zoom)
    height = width / aspect
    x = min(max(center_x * source_width - width / 2, 0), source_width - width)
    y = min(max(center_y * source_height - height / 2, 0), source_height - height)
    return x, y, width, height


def camera_angles(center_x, center_y, zoom):
    yaw = ((center_x % 1) - .5) * math.tau
    pitch = min(max((.5 - center_y) * math.pi, -PITCH_LIMIT), PITCH_LIMIT)
    tangent = math.tan(math.radians(BASE_FOV / 2)) / zoom
    return yaw, pitch, tangent


def spherical_uv(screen_x, screen_y, aspect, center_x, center_y, zoom, camera_height=0):
    """Perspective ray -> top-left-origin panorama UV; reference implementation."""
    yaw, pitch, tangent = camera_angles(center_x, center_y, zoom)
    x, y = screen_x * tangent * aspect, -screen_y * tangent
    py = y * math.cos(pitch) + math.sin(pitch)
    pz = -y * math.sin(pitch) + math.cos(pitch)
    wx = x * math.cos(yaw) + pz * math.sin(yaw)
    wz = -x * math.sin(yaw) + pz * math.cos(yaw)
    norm = math.sqrt(x * x + y * y + 1)
    if camera_height:
        dx, dy, dz = wx / norm, py / norm, wz / norm
        distance = -camera_height * dy + math.sqrt(1 - camera_height**2 + (camera_height * dy)**2)
        wx, py, wz = distance * dx, camera_height + distance * dy, distance * dz
        norm = 1.0
    u = (math.atan2(wx, wz) / math.tau + .5) % 1
    v = .5 - math.asin(min(max(py / norm, -1), 1)) / math.pi
    return u, v


def pan_sphere(center_x, center_y, zoom, dx, dy, viewport_width, viewport_height, aspect):
    yaw, pitch, tangent = camera_angles(center_x, center_y, zoom)
    yaw -= dx / viewport_width * 2 * math.atan(tangent * aspect)
    pitch += dy / viewport_height * 2 * math.atan(tangent)
    pitch = min(max(pitch, -PITCH_LIMIT), PITCH_LIMIT)
    return (yaw / math.tau + .5) % 1, .5 - pitch / math.pi
