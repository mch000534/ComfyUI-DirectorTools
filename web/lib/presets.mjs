import { cameraAngles, RATIOS, BASE_FOV, MIN_ZOOM, MAX_ZOOM, wrap } from './geometry.mjs?v=0.8.3';

export const MAX_FOV = 2*Math.atan(Math.tan(BASE_FOV*Math.PI/360)/MIN_ZOOM)*180/Math.PI;
export const MIN_FOV = 2*Math.atan(Math.tan(BASE_FOV*Math.PI/360)/MAX_ZOOM)*180/Math.PI;
export function framingDegrees(cx,cy,zoom) {
    const a = cameraAngles(cx,cy,zoom);
    return {yaw:a.yaw*180/Math.PI,pitch:a.pitch*180/Math.PI,vertical_fov:2*Math.atan(a.tangent)*180/Math.PI};
}
export function degreeFraming(yaw,pitch,vertical_fov) {
    for (const [name,value,low,high] of [['yaw',yaw,-180,180],['pitch',pitch,-89.9,89.9],['vertical_fov',vertical_fov,MIN_FOV-1e-9,MAX_FOV+1e-9]]) {
        if (typeof value !== 'number' || !Number.isFinite(value) || value<low || value>high) throw new Error(`${name} must be ${low.toFixed(3)}–${high.toFixed(3)}.`);
    }
    return {center_x:wrap(yaw/360+.5),center_y:.5-pitch/180,zoom:Math.min(MAX_ZOOM,Math.max(MIN_ZOOM,Math.tan(BASE_FOV*Math.PI/360)/Math.tan(vertical_fov*Math.PI/360)))};
}
export function parsePresets(text) {
    if (typeof text !== 'string' || text.length>262144) throw new Error('Preset JSON must be at most 256 KiB.');
    const doc = JSON.parse(text);
    if (!doc || doc.schema_version!==1 || !Array.isArray(doc.shots) || doc.shots.length<1 || doc.shots.length>64) throw new Error('Expected schema_version 1 and 1–64 shots.');
    const ids = new Set(), sources = new Set();
    let pixels = 0;
    const shots = doc.shots.map(s=> {
        if (!s || typeof s!=='object') throw new Error('Invalid shot.');
        for (const key of ['shot_id','name','source_id']) {
            if (typeof s[key]!=='string' || !s[key].trim() || s[key].length>80 || /[\u0000-\u001f\u007f]/.test(s[key])) throw new Error(`${key} must be 1–80 characters.`);
        }
        if (!/^[A-Za-z0-9_-]+$/.test(s.shot_id) || ids.has(s.shot_id.toLowerCase())) throw new Error('Shot IDs must be unique letters, numbers, underscores or hyphens (ignoring case).');
        ids.add(s.shot_id.toLowerCase()); sources.add(s.source_id);
        degreeFraming(s.yaw,s.pitch,s.vertical_fov);
        for (const key of ['width','height']) if (!Number.isInteger(s[key]) || s[key]<1 || s[key]>8192) throw new Error(`${key} must be 1–8192.`);
        if (typeof s.aspect_ratio!=='string' || (!Object.hasOwn(RATIOS,s.aspect_ratio) && s.aspect_ratio!=='Free')) throw new Error('Unknown aspect ratio.');
        const ratio = RATIOS[s.aspect_ratio];
        if (ratio && Math.abs(s.width-s.height*ratio)>Math.max(1,ratio)/2+1e-7) throw new Error('Dimensions do not match the aspect ratio.');
        if (typeof s.camera_height!=='number' || !Number.isFinite(s.camera_height) || Math.abs(s.camera_height)>.8) throw new Error('Camera height must be -0.8–0.8.');
        pixels += s.width*s.height;
        return Object.fromEntries(['shot_id','name','source_id','yaw','pitch','vertical_fov','width','height','aspect_ratio','camera_height'].map(k=>[k,s[k]]));
    });
    if (sources.size!==1) throw new Error('Use one source_id per panorama document.');
    if (pixels>33554432) throw new Error('Batch exceeds 32 megapixels; split the shot list.');
    return {schema_version:1,shots};
}

// Keep the chosen prefix and padding; Add never replaces an existing shot.
export function nextShotID(current,shots) {
    const id=current.trim() || 'SH000';
    const match=/^(.*?)([0-9]+)$/.exec(id);
    const prefix=match?match[1]:id;
    const digits=match?match[2]:'000';
    const occupied=new Set(shots.map(s=>s.shot_id.toLowerCase()));
    let number=BigInt(digits), next;
    do {next=prefix+String(++number).padStart(digits.length,'0');}
    while(occupied.has(next.toLowerCase()));
    return next;
}

export function renumberShots(shots) {
    return shots.map((shot,index)=>({...shot,shot_id:`SH${String(index+1).padStart(3,'0')}`}));
}
