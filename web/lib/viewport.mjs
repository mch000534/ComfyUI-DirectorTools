import { cameraAngles, clamp, cropRect, MIN_ZOOM, MAX_ZOOM, panCenter, panSphere } from './geometry.mjs?v=0.8.3';
import { PanoramaRenderer } from './panorama_renderer.mjs?v=0.8.3';
import { createShotControls } from './shot_controls.mjs?v=0.8.3';

export function createViewport(node, api) {
    const controller = new AbortController();
    const root = document.createElement('div');
    root.className = 'director-tools-panorama-viewport';
    root.style.cssText = 'width:100%;height:604px;box-sizing:border-box;padding:8px;background:#171b22;color:#e5e9f0;border-radius:8px;font:12px system-ui;display:flex;flex-direction:column;gap:6px;overflow:hidden;';
    const bar = document.createElement('div');
    bar.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:8px;';
    const title = document.createElement('span');
    title.textContent = 'VIRTUAL CAMERA · source from last run';
    title.style.cssText = 'font-size:10px;letter-spacing:.7px;color:#a7b3c5;';
    const reset = document.createElement('button');
    reset.textContent = 'Reset framing';
    reset.style.cssText = 'background:#303b4d;color:#fff;border:1px solid #506079;border-radius:4px;padding:4px 8px;cursor:pointer;font:inherit;';
    bar.append(title, reset);
    const canvas = document.createElement('canvas');
    canvas.setAttribute('aria-label', 'Camera viewport. Drag to pan, scroll to zoom. Arrow keys pan; plus and minus zoom.');
    canvas.setAttribute('role', 'img');
    canvas.tabIndex = 0;
    canvas.style.cssText = 'width:100%;height:246px;min-height:246px;display:block;touch-action:none;cursor:grab;outline-offset:-2px;';
    const stage = document.createElement('div');
    stage.style.cssText = 'position:relative;width:100%;height:246px;min-height:246px;background:#101319;';
    const sphericalCanvas = document.createElement('canvas');
    sphericalCanvas.setAttribute('aria-hidden','true');
    sphericalCanvas.style.cssText = 'position:absolute;pointer-events:none;display:none;';
    canvas.style.position = 'absolute'; canvas.style.inset = '0';
    stage.append(sphericalCanvas,canvas);
    const status = document.createElement('div');
    status.setAttribute('role', 'status');
    status.style.cssText = 'font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
    const hint = document.createElement('div');
    hint.textContent = 'Drag image · Scroll to zoom · Run again to render changes';
    hint.style.cssText = 'font-size:10px;color:#a7b3c5;';
    root.append(bar, stage, status, hint);
    let source = null, meta = null, frame = null, gesture = null;
    let renderer = null, rendererError = null, contextLost = false;
    let pending = 0, generation = 0, disposed = false;
    const widget = name => node.widgets.find(w => w.name === name);
    const value = name => Number(widget(name)?.value);
    const controls=createShotControls(node,dirty);
    root.append(controls.element);
    function write(name, v) { widget(name).value = v; }
    function settings() {
        const width = value('width'), height = value('height');
        return { width, height, cx: value('center_x'), cy: value('center_y'), zoom: value('zoom'), cameraHeight: value('camera_height') || 0,
                 spherical: widget('projection')?.value === '360 Panorama' };
    }
    function rect() {
        const s = settings();
        return cropRect(meta.source_width, meta.source_height, s.width / s.height, s.cx, s.cy, s.zoom);
    }
    function dirty() {
        node.setDirtyCanvas?.(true, true);
        node.graph?.change?.();
        sync();
    }
    function sync() {
        controls.sync();
        if (!disposed && !pending) pending = requestAnimationFrame(draw);
    }
    function draw() {
        pending = 0;
        if (disposed) return;
        const width = canvas.clientWidth || 320, height = canvas.clientHeight || 246;
        const dpr = window.devicePixelRatio || 1;
        canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        ctx.fillStyle = '#101319'; ctx.fillRect(0, 0, width, height);
        sphericalCanvas.style.display = 'none';
        if (!source || !meta) {
            ctx.fillStyle = '#a7b3c5'; ctx.textAlign = 'center'; ctx.font = '12px system-ui';
            ctx.fillText('Run workflow to load the input image', width / 2, height / 2);
            frame = null;
            return;
        }
        const s = settings();
        title.textContent = s.spherical ? 'VIRTUAL CAMERA · 360° panorama' : 'VIRTUAL CAMERA · flat crop';
        const aspect = s.width / s.height;
        const fw = Math.min(width - 24, (height - 24) * aspect), fh = fw / aspect;
        frame = { x: (width - fw) / 2, y: (height - fh) / 2, width: fw, height: fh };
        if (s.spherical) {
            if (!renderer && !rendererError && !contextLost) {
                try { renderer = new PanoramaRenderer(sphericalCanvas); renderer.upload(source); }
                catch (error) { rendererError = error.message; }
            }
            if (renderer && !contextLost) {
                Object.assign(sphericalCanvas.style,{display:'block',left:`${frame.x}px`,top:`${frame.y}px`,width:`${fw}px`,height:`${fh}px`});
                renderer.render({...s,aspect},Math.max(1,Math.round(fw*dpr)),Math.max(1,Math.round(fh*dpr)));
                ctx.clearRect(frame.x,frame.y,fw,fh);
            } else {
                status.textContent = contextLost ? 'Preview context lost. Waiting for browser recovery…' : rendererError;
                return;
            }
        } else {
            const r = rect();
            ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
            ctx.drawImage(source,
                r.x * source.naturalWidth / meta.source_width,
                r.y * source.naturalHeight / meta.source_height,
                r.width * source.naturalWidth / meta.source_width,
                r.height * source.naturalHeight / meta.source_height,
                frame.x, frame.y, fw, fh);
        }
        ctx.strokeStyle = '#ffffff55'; ctx.lineWidth = 1;
        ctx.beginPath();
        for (const n of [1, 2]) {
            ctx.moveTo(frame.x + fw * n / 3, frame.y); ctx.lineTo(frame.x + fw * n / 3, frame.y + fh);
            ctx.moveTo(frame.x, frame.y + fh * n / 3); ctx.lineTo(frame.x + fw, frame.y + fh * n / 3);
        }
        ctx.stroke(); ctx.strokeStyle = '#7dd3fc'; ctx.lineWidth = 2;
        ctx.strokeRect(frame.x, frame.y, fw, fh);
        const angles = cameraAngles(s.cx,s.cy,s.zoom);
        status.textContent = s.spherical
            ? `${meta.source_width} × ${meta.source_height} → ${s.width} × ${s.height} · VFOV ${(2*Math.atan(angles.tangent)*180/Math.PI).toFixed(1)}° · Height ${s.cameraHeight >= 0 ? '+' : ''}${s.cameraHeight.toFixed(2)}`
            : `${meta.source_width} × ${meta.source_height} → ${s.width} × ${s.height} · Zoom ${s.zoom.toFixed(2)}×`;
    }
    function point(event) {
        const bounds = canvas.getBoundingClientRect();
        return { x: (event.clientX - bounds.x) * canvas.clientWidth / bounds.width,
                 y: (event.clientY - bounds.y) * canvas.clientHeight / bounds.height };
    }
    function inside(p) {
        return frame && p.x >= frame.x && p.x <= frame.x + frame.width && p.y >= frame.y && p.y <= frame.y + frame.height;
    }
    const listen = (element, type, handler, options = {}) => element.addEventListener(type, handler, { ...options, signal: controller.signal });
    listen(sphericalCanvas,'webglcontextlost',event => {
        event.preventDefault(); contextLost = true; endGesture(); sync();
    });
    listen(sphericalCanvas,'webglcontextrestored',() => {
        renderer?.destroy(); renderer = null; rendererError = null; contextLost = false; sync();
    });
    listen(canvas, 'pointerdown', event => {
        if (event.button !== 0 || !source || !inside(point(event))) return;
        event.preventDefault(); event.stopPropagation(); canvas.focus();
        node.graph?.beforeChange?.();
        gesture = { id: event.pointerId, point: point(event), rect: rect(), frame: { ...frame }, settings: settings() };
        canvas.setPointerCapture(event.pointerId); canvas.style.cursor = 'grabbing';
    });
    listen(canvas, 'pointermove', event => {
        if (!gesture || gesture.id !== event.pointerId) return;
        event.preventDefault(); event.stopPropagation();
        const p = point(event);
        const s = gesture.settings;
        const center = s.spherical
            ? panSphere(s.cx,s.cy,s.zoom,p.x-gesture.point.x,p.y-gesture.point.y,gesture.frame.width,gesture.frame.height,s.width/s.height)
            : panCenter(gesture.rect, meta.source_width, meta.source_height,
                p.x - gesture.point.x, p.y - gesture.point.y, gesture.frame.width, gesture.frame.height);
        write('center_x', center.x); write('center_y', center.y); dirty();
    });
    function endGesture() {
        if (!gesture) return;
        const id = gesture.id;
        gesture = null;
        if (canvas.hasPointerCapture(id)) canvas.releasePointerCapture(id);
        canvas.style.cursor = 'grab'; node.graph?.afterChange?.();
    }
    function finish(event) {
        if (!gesture || event.pointerId !== gesture.id) return;
        event.stopPropagation(); endGesture(); dirty();
    }
    listen(canvas, 'pointerup', finish); listen(canvas, 'pointercancel', finish); listen(canvas, 'lostpointercapture', finish);
    function changeZoom(factor) {
        if (!source) return;
        if (settings().spherical) {
            write('zoom',clamp(value('zoom')*factor,MIN_ZOOM,MAX_ZOOM)); dirty(); return;
        }
        const r = rect();
        write('center_x', (r.x + r.width / 2) / meta.source_width);
        write('center_y', (r.y + r.height / 2) / meta.source_height);
        write('zoom', clamp(value('zoom') * factor, MIN_ZOOM, MAX_ZOOM));
        const next = rect();
        write('center_x', (next.x + next.width / 2) / meta.source_width);
        write('center_y', (next.y + next.height / 2) / meta.source_height);
        dirty();
    }
    listen(canvas, 'wheel', event => {
        // Keep scroll inside the widget even while the source is loading.
        event.preventDefault(); event.stopPropagation();
        if (!source) return;
        const units = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? 246 : 1;
        node.graph?.beforeChange?.();
        changeZoom(Math.exp(clamp(-event.deltaY * units * .002, -1, 1)));
        node.graph?.afterChange?.();
    }, { passive: false });
    listen(canvas, 'keydown', event => {
        if (!source || !['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(event.key)) return;
        event.preventDefault(); event.stopPropagation(); node.graph?.beforeChange?.();
        if (['+','=','-'].includes(event.key)) changeZoom(event.key === '-' ? 1 / 1.1 : 1.1);
        else {
            const r = rect(), s = settings(), step = event.shiftKey ? .1 : .02;
            const dx = event.key === 'ArrowLeft' ? step : event.key === 'ArrowRight' ? -step : 0;
            const dy = event.key === 'ArrowUp' ? step : event.key === 'ArrowDown' ? -step : 0;
            const center = s.spherical ? panSphere(s.cx,s.cy,s.zoom,dx,dy,1,1,s.width/s.height)
                : panCenter(r, meta.source_width, meta.source_height, dx, dy, 1, 1);
            write('center_x', center.x); write('center_y', center.y); dirty();
        }
        node.graph?.afterChange?.();
    });
    listen(reset, 'pointerdown', event => event.stopPropagation());
    listen(reset, 'click', event => {
        event.stopPropagation(); node.graph?.beforeChange?.();
        write('center_x', .5); write('center_y', .5); write('zoom', 1); write('camera_height', 0);
        dirty(); node.graph?.afterChange?.();
    });
    const observer = new ResizeObserver(sync); observer.observe(canvas);
    function clear(message = 'Run workflow to load the input image') {
        endGesture();
        generation++; source = null; meta = null; frame = null;
        canvas.style.cursor = 'grab'; status.textContent = message; sync();
    }
    function loadPreview(data) {
        if (disposed) return;
        if (!data || data.type !== 'temp' || data.subfolder !== '' ||
            !/^director_tools_panorama_[a-f0-9]{32}\.png$/.test(data.filename) ||
            !Number.isInteger(data.source_width) || data.source_width < 1 ||
            !Number.isInteger(data.source_height) || data.source_height < 1) {
            clear(); return;
        }
        endGesture();
        const serial = ++generation;
        source = null; meta = null; frame = null; status.textContent = 'Loading source preview…'; sync();
        const image = new Image();
        image.onload = () => {
            if (disposed || serial !== generation) return;
            source = image; meta = data;
            if (renderer && !contextLost) renderer.upload(image);
            sync();
        };
        image.onerror = () => {
            if (!disposed && serial === generation) clear('Preview expired. Run workflow to reload the image.');
        };
        const query = new URLSearchParams({filename:data.filename,subfolder:'',type:'temp'});
        image.src = api.apiURL(`/view?${query}`);
    }
    function destroy() {
        if (disposed) return;
        endGesture(); disposed = true; generation++;
        controller.abort(); observer.disconnect(); cancelAnimationFrame(pending);
        controls.destroy();
        renderer?.destroy(); renderer = null;
        source = null; meta = null;
    }
    clear();
    return { element: root, sync, clear, loadPreview, destroy, restore: controls.restore };
}
