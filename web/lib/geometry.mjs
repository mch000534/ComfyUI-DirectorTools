// Source edge coordinates, identical to geometry.py. No browser dependencies.
export const RATIOS = Object.freeze({
    '16:9': 16 / 9, '9:16': 9 / 16, '1:1': 1,
    '4:3': 4 / 3, '3:2': 3 / 2, '2.39:1': 2.39,
});
export const MAX_SIZE = 8192;
export const MIN_ZOOM = 0.5;
export const MAX_ZOOM = 32;
export const BASE_FOV = 75;
export const PITCH_LIMIT = 89.9 * Math.PI / 180;
export const clamp = (value, low, high) => Math.min(Math.max(value, low), high);
export const wrap = value => ((value % 1) + 1) % 1;

export function cropRect(sw, sh, aspect, cx, cy, zoom) {
    const width = Math.min(sw, sh * aspect) / Math.max(1, zoom);
    const height = width / aspect;
    return {
        x: clamp(cx * sw - width / 2, 0, sw - width),
        y: clamp(cy * sh - height / 2, 0, sh - height),
        width, height,
    };
}

export function syncedSize(aspect, width, height, edited = 'width') {
    width = clamp(Math.round(width), 1, MAX_SIZE);
    height = clamp(Math.round(height), 1, MAX_SIZE);
    const ratio = RATIOS[aspect];
    if (!ratio) return [width, height];
    if (edited === 'height') {
        width = Math.max(1, Math.round(height * ratio));
        if (width > MAX_SIZE) {
            width = MAX_SIZE;
            height = Math.max(1, Math.round(width / ratio));
        }
    } else {
        height = Math.max(1, Math.round(width / ratio));
        if (height > MAX_SIZE) {
            height = MAX_SIZE;
            width = Math.max(1, Math.round(height * ratio));
        }
    }
    return [width, height];
}

export function panCenter(rect, sw, sh, dx, dy, viewportWidth, viewportHeight) {
    const x = clamp(rect.x - dx * rect.width / viewportWidth, 0, sw - rect.width);
    const y = clamp(rect.y - dy * rect.height / viewportHeight, 0, sh - rect.height);
    return { x: (x + rect.width / 2) / sw, y: (y + rect.height / 2) / sh };
}

export function cameraAngles(cx, cy, zoom) {
    return {
        yaw: (wrap(cx) - .5) * 2 * Math.PI,
        pitch: clamp((.5 - cy) * Math.PI, -PITCH_LIMIT, PITCH_LIMIT),
        tangent: Math.tan(BASE_FOV * Math.PI / 360) / zoom,
    };
}

export function sphericalUV(screenX, screenY, aspect, cx, cy, zoom, cameraHeight = 0) {
    const {yaw, pitch, tangent} = cameraAngles(cx, cy, zoom);
    const x = screenX * tangent * aspect, y = -screenY * tangent;
    let py = y * Math.cos(pitch) + Math.sin(pitch);
    const pz = -y * Math.sin(pitch) + Math.cos(pitch);
    let wx = x * Math.cos(yaw) + pz * Math.sin(yaw);
    let wz = -x * Math.sin(yaw) + pz * Math.cos(yaw);
    let norm = Math.sqrt(x*x+y*y+1);
    if (cameraHeight) {
        const dx=wx/norm, dy=py/norm, dz=wz/norm;
        const distance=-cameraHeight*dy+Math.sqrt(1-cameraHeight*cameraHeight+(cameraHeight*dy)**2);
        wx=distance*dx; py=cameraHeight+distance*dy; wz=distance*dz; norm=1;
    }
    return {
        u: wrap(Math.atan2(wx, wz) / (2 * Math.PI) + .5),
        v: .5 - Math.asin(clamp(py / norm, -1, 1)) / Math.PI,
    };
}

export function panSphere(cx, cy, zoom, dx, dy, viewportWidth, viewportHeight, aspect) {
    const {yaw, pitch, tangent} = cameraAngles(cx, cy, zoom);
    return {
        x: wrap((yaw - dx / viewportWidth * 2 * Math.atan(tangent * aspect)) / (2 * Math.PI) + .5),
        y: .5 - clamp(pitch + dy / viewportHeight * 2 * Math.atan(tangent), -PITCH_LIMIT, PITCH_LIMIT) / Math.PI,
    };
}
