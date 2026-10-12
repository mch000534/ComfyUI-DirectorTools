// Requires an isolated ComfyUI instance with test-panorama.png in input.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile} from 'node:fs/promises';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.COMFY_TEST_URL||'http://127.0.0.1:8199';
const workflow=JSON.parse(await readFile(new URL('../example_workflows/director_tools_panorama_shift.json',import.meta.url)));
const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'chrome'});
try{
    const page=await browser.newPage({viewport:{width:1600,height:1050}});
    await page.goto(base);
    await page.waitForFunction(()=>window.app&&window.LiteGraph?.registered_node_types?.DirectorToolsPanoramaShift);
    await page.waitForLoadState('networkidle');
    await page.evaluate(async data=>window.app.loadGraphData(data),workflow);
    const state=await page.evaluate(async()=>{
        const node=window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaShift');
        return {ports:node.outputs.map(o=>[o.name,o.type]),prompt:(await window.app.graphToPrompt()).output};
    });
    assert.deepEqual(state.ports,[['image','IMAGE'],['prompt','STRING']]);
    assert.equal(state.prompt['2'].inputs.shift_x,.5);
    assert.deepEqual(state.prompt['3'].inputs.images,['2',0]);
    assert.deepEqual(state.prompt['4'].inputs.source,['2',1]);
    const previous=Object.keys(await(await fetch(`${base}/history`)).json());
    await page.evaluate(async()=>window.app.queuePrompt(0,1));
    const deadline=Date.now()+30000;
    let completed;
    while(Date.now()<deadline){
        const history=await(await fetch(`${base}/history`,{cache:'no-store'})).json();
        completed=Object.entries(history).find(([id,h])=>!previous.includes(id)&&h.prompt[2]['2']?.class_type==='DirectorToolsPanoramaShift')?.[1];
        if(completed)break;
        await new Promise(r=>setTimeout(r,100));
    }
    assert.ok(completed,'Shift workflow completed');
    assert.equal(completed.status.status_str,'success');
    assert.equal(completed.outputs['3'].images.length,1);
    assert.ok(completed.outputs['4'].text[0].includes('x=1000 pixels'));
    console.log('ComfyUI frontend: Panorama Shift workflow imports, exposes IMAGE/STRING ports and executes connected consumers.');
}finally{await browser.close();}
