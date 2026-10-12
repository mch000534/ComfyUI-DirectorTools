import { degreeFraming, framingDegrees, MAX_FOV, MIN_FOV, nextShotID, parsePresets, renumberShots } from './presets.mjs?v=0.8.3';

// Auxiliary controls live in a non-serialized DOM widget. Camera inputs remain
// the sole rendering state; presets are saved in standard node properties.
export function createShotControls(node, changed) {
    const controller=new AbortController();
    const root=document.createElement('div');
    root.style.cssText='display:flex;flex-direction:column;gap:6px;font:11px system-ui;';
    const style='box-sizing:border-box;min-width:0;background:#263142;color:#e5e9f0;border:1px solid #506079;border-radius:4px;padding:4px;font:inherit;';
    const widget=name=>node.widgets.find(w=>w.name===name);
    const listen=(element,type,handler)=>element.addEventListener(type,handler,{signal:controller.signal});
    const row=()=>{const e=document.createElement('div');e.style.cssText='display:flex;gap:5px;align-items:center;';root.append(e);return e;};
    function field(parent,label,type='text',initial='') {
        const wrap=document.createElement('label');wrap.style.cssText='display:flex;flex:1;min-width:0;flex-direction:column;gap:2px;';
        const text=document.createElement('span');text.textContent=label;
        const input=document.createElement('input');input.type=type;input.value=initial;input.setAttribute('aria-label',label);input.style.cssText=style+'width:100%;';
        wrap.append(text,input);parent.append(wrap);return input;
    }
    function button(parent,label,action) {
        const e=document.createElement('button');e.type='button';e.textContent=label;e.style.cssText=style+'cursor:pointer;';
        listen(e,'click',async()=>{try{await action();}catch(error){message.textContent=error.message;}});parent.append(e);return e;
    }
    function mutate(action) {
        node.graph?.beforeChange?.();
        try{action();node.setDirtyCanvas?.(true,true);node.graph?.change?.();changed();}
        finally{node.graph?.afterChange?.();}
    }
    const angleRow=row();
    const yaw=field(angleRow,'Yaw (degrees)','number','0');
    const pitch=field(angleRow,'Pitch (degrees)','number','0');
    const fov=field(angleRow,'Vertical FOV (degrees)','number','75');
    yaw.min=-180;yaw.max=180;pitch.min=-89.9;pitch.max=89.9;fov.min=MIN_FOV;fov.max=MAX_FOV;
    for (const input of [yaw,pitch,fov]) {
        input.step='any';
        listen(input,'change',()=>{
            try {
                if (![yaw,pitch,fov].every(e=>e.value.trim())) throw new Error('Enter all three camera angles.');
                const framing=degreeFraming(Number(yaw.value),Number(pitch.value),Number(fov.value));
                mutate(()=>{for (const [key,value] of Object.entries(framing)) widget(key).value=value;});
                message.textContent='Camera updated. Run again to render.';
            }catch(error){message.textContent=error.message;sync(true);}
        });
    }
    const idRow=row();
    const shotID=field(idRow,'Shot ID','text','SH010');
    const nameWrap=document.createElement('div');
    nameWrap.style.cssText='display:flex;flex:1;min-width:0;flex-direction:column;gap:2px;';
    idRow.append(nameWrap);
    const nameLabel=document.createElement('label');nameLabel.style.cssText='display:flex;flex-direction:column;gap:2px;';
    const nameText=document.createElement('span');nameText.textContent='Shot name';
    const nameSelect=document.createElement('select');nameSelect.setAttribute('aria-label','Shot name');nameSelect.style.cssText=style+'width:100%;';
    const commonNames=[
        ['Establishing','Establishing · 建立鏡頭'],
        ['Extreme wide','Extreme wide · 大遠景'],
        ['Wide','Wide · 全景'],
        ['Full','Full · 全身'],
        ['Medium wide','Medium wide · 中遠景'],
        ['Medium','Medium · 中景'],
        ['Medium close-up','Medium close-up · 中近景'],
        ['Close-up','Close-up · 特寫'],
        ['Extreme close-up','Extreme close-up · 大特寫'],
        ['Over-the-shoulder','Over-the-shoulder · 過肩'],
        ['POV','POV · 主觀視角'],
        ['Two-shot','Two-shot · 雙人鏡頭'],
        ['Insert','Insert · 插入鏡頭'],
        ['Detail','Detail · 細節'],
        ['__custom__','Custom · 自訂'],
    ];
    for(const [value,label] of commonNames){const option=document.createElement('option');option.value=value;option.textContent=label;nameSelect.append(option);}
    nameSelect.value='Wide';nameLabel.append(nameText,nameSelect);nameWrap.append(nameLabel);
    const customWrap=document.createElement('div');nameWrap.append(customWrap);
    const name=field(customWrap,'Custom shot name','text','');
    function nameMode(){customWrap.hidden=nameSelect.value!=='__custom__';}
    function setShotName(value){
        if(commonNames.some(([id])=>id!=='__custom__' && id===value))nameSelect.value=value;
        else {nameSelect.value='__custom__';name.value=value;}
        nameMode();
    }
    const shotName=()=>nameSelect.value==='__custom__'?name.value.trim():nameSelect.value;
    listen(nameSelect,'input',nameMode);listen(nameSelect,'change',nameMode);nameMode();
    const sourceID=field(idRow,'Source ID','text','panorama_A');
    for(const input of [shotID,name,sourceID])input.maxLength=80;
    const presetRow=row();
    const select=document.createElement('select');select.setAttribute('aria-label','Saved shots');select.style.cssText=style+'flex:1;';presetRow.append(select);
    const documentJSON=()=>JSON.stringify({schema_version:1,shots},null,2);
    let shots=[];
    function persist(){node.properties??={};node.properties.director_tools_shots=JSON.parse(documentJSON());}
    function options(selected=select.value){
        select.replaceChildren();
        for(const shot of shots){const option=document.createElement('option');option.value=shot.shot_id;option.textContent=`${shot.shot_id} · ${shot.name}`;select.append(option);}
        if(shots.some(s=>s.shot_id===selected))select.value=selected;
    }
    function populate(){
        const s=shots.find(s=>s.shot_id===select.value);
        if(s){shotID.value=s.shot_id;setShotName(s.name);sourceID.value=s.source_id;}
    }
    function applyPreset(){
        const shot=shots.find(s=>s.shot_id===select.value);
        if(!shot)throw new Error('Save or import a preset first.');
        const values={...degreeFraming(shot.yaw,shot.pitch,shot.vertical_fov),projection:'360 Panorama'};
        for(const key of ['width','height','aspect_ratio','camera_height'])values[key]=shot[key];
        // input and change may both fire for one native selection. Mutate once.
        if(Object.entries(values).some(([key,value])=>widget(key).value!==value)){
            mutate(()=>{for(const [key,value] of Object.entries(values))widget(key).value=value;populate();});
        }else populate();
        message.textContent=`Applied ${shot.shot_id}. Run again to render.`;
    }
    const selectionChanged=()=>{
        try{applyPreset();}catch(error){message.textContent=error.message;}
    };
    listen(select,'input',selectionChanged);
    listen(select,'change',selectionChanged);
    button(presetRow,'Add preset',()=>savePreset(true));
    button(presetRow,'Save preset',()=>savePreset(false));
    function savePreset(add){
        if(widget('projection').value!=='360 Panorama')throw new Error('Switch to 360 Panorama before saving a camera preset.');
        const degrees=framingDegrees(Number(widget('center_x').value),Number(widget('center_y').value),Number(widget('zoom').value));
        const shot={shot_id:add?nextShotID(shotID.value,shots):shotID.value.trim(),name:shotName(),source_id:sourceID.value.trim(),...degrees};
        for(const key of ['width','height','aspect_ratio','camera_height'])shot[key]=widget(key).value;
        const next=shots.filter(s=>s.shot_id!==shot.shot_id);
        const index=shots.findIndex(s=>s.shot_id===shot.shot_id);
        if(index<0)next.push(shot);else next.splice(index,0,shot);
        const valid=parsePresets(JSON.stringify({schema_version:1,shots:next}));
        mutate(()=>{shots=valid.shots;persist();options(shot.shot_id);populate();});
        message.textContent=`Saved ${shot.shot_id}${index<0?'':' (replaced)'}.`;
    }
    button(presetRow,'Delete',()=>{
        const id=select.value;if(!id)return;
        mutate(()=>{shots=shots.filter(s=>s.shot_id!==id);persist();options();populate();});
        message.textContent=`Deleted ${id}.`;
    });
    const jsonRow=row();
    const json=document.createElement('textarea');json.setAttribute('aria-label','Preset JSON');json.placeholder='Preset JSON · paste here to import';json.style.cssText=style+'width:100%;height:44px;resize:none;';jsonRow.append(json);
    const actions=row();
    button(actions,'Reset Shot ID',()=>{
        const selectedIndex=shots.findIndex(s=>s.shot_id===select.value);
        const renumbered=renumberShots(shots);
        const valid=renumbered.length?parsePresets(JSON.stringify({schema_version:1,shots:renumbered})).shots:[];
        mutate(()=>{
            shots=valid;persist();
            const selected=shots[Math.max(0,selectedIndex)];
            options(selected?.shot_id);
            shotID.value=selected?.shot_id || 'SH000';
            json.value=documentJSON();
        });
        message.textContent=shots.length?`Renumbered ${shots.length} shots from SH001.`:'Shot IDs reset. Add preset starts at SH001.';
    }).title='Renumber all saved shots in list order from SH001.';
    button(actions,'Copy JSON',async()=>{
        parsePresets(documentJSON());json.value=documentJSON();json.focus();json.select();
        try{
            await navigator.clipboard.writeText(json.value);
            if(!controller.signal.aborted)message.textContent='JSON copied. Paste into Batch Panorama.';
        }catch{
            if(!controller.signal.aborted)message.textContent='JSON selected. Press Copy and paste into Batch Panorama.';
        }
    });
    button(actions,'Export JSON',()=>{
        parsePresets(documentJSON());
        const url=URL.createObjectURL(new Blob([documentJSON()],{type:'application/json'}));
        const a=document.createElement('a');a.href=url;a.download='camera_presets.json';a.click();
        setTimeout(()=>URL.revokeObjectURL(url),1000);
        message.textContent='Exported camera_presets.json.';
    });
    function importText(text){
        const valid=parsePresets(text);
        mutate(()=>{shots=valid.shots;persist();options();populate();json.value=documentJSON();});
        message.textContent=`Imported ${shots.length} shots. Select one to update the camera.`;
    }
    button(actions,'Import JSON',()=>importText(json.value));
    const file=document.createElement('input');file.type='file';file.accept='.json,application/json';file.hidden=true;root.append(file);
    button(actions,'Open JSON file',()=>file.click());
    listen(file,'change',async()=>{
        try{
            const selected=file.files?.[0];if(!selected)return;
            if(selected.size>1048576)throw new Error('JSON file is too large.');
            const text=await selected.text();if(!controller.signal.aborted)importText(text);
        }catch(error){message.textContent=error.message;}
        finally{file.value='';}
    });
    const message=document.createElement('div');message.setAttribute('role','alert');message.style.cssText='min-height:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#a7b3c5;';root.append(message);
    for(const type of ['pointerdown','wheel','keydown'])listen(root,type,event=>event.stopPropagation());
    function sync(force=false){
        const spherical=widget('projection')?.value==='360 Panorama';
        const a=framingDegrees(Number(widget('center_x').value),Number(widget('center_y').value),Number(widget('zoom').value));
        for(const [input,key] of [[yaw,'yaw'],[pitch,'pitch'],[fov,'vertical_fov']]){
            input.disabled=!spherical;
            // Preserve full precision in values; rounding narrow FOV could exceed zoom 32.
            if(force || document.activeElement!==input)input.value=String(Number(a[key].toPrecision(12)));
        }
    }
    function restore(){
        const saved=node.properties?.director_tools_shots;
        try{
            shots=saved?.schema_version===1 && Array.isArray(saved.shots) && saved.shots.length===0 ? [] : saved?parsePresets(JSON.stringify(saved)).shots:[];
            options();populate();sync();message.textContent='Source ID identifies this panorama; presets do not load source images.';
        }catch(error){shots=[];options();message.textContent=`Saved presets could not load: ${error.message}`;}
    }
    restore();
    return {element:root,sync,restore,destroy:()=>controller.abort()};
}
