// Requires an isolated ComfyUI instance on COMFY_TEST_URL (default :8199).
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.COMFY_TEST_URL || 'http://127.0.0.1:8199';
async function completedAfter(previousIDs,nodeType) {
    const deadline=Date.now()+30000;
    while(Date.now()<deadline) {
        const h=await(await fetch(`${base}/history`,{cache:'no-store'})).json();
        const entry=Object.entries(h).find(([id,result])=>!previousIDs.includes(id)&&result.prompt[2]['2']?.class_type===nodeType)?.[1];
        if(entry)return entry;
        await new Promise(resolve=>setTimeout(resolve,100));
    }
    throw new Error(`No completed ${nodeType} execution within 30 seconds.`);
}
const workflow = JSON.parse(await readFile(new URL('../example_workflows/director_tools_panorama.json', import.meta.url)));
// Emulate an old saved workflow with only the original IMAGE output slot.
workflow.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').outputs=workflow.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').outputs.slice(0,1);
const browser = await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL || 'chrome'});
try {
    const page = await browser.newPage({viewport:{width:1600,height:1050}});
    const errors=[];
    page.on('pageerror', e=>errors.push(e.message));
    await page.goto(base);
    await page.waitForFunction(() => Boolean(window.app));
    await page.evaluate(() => { window.testApp = window.app; });
    await page.waitForFunction(() => window.app===window.testApp && window.LiteGraph?.registered_node_types?.DirectorToolsPanoramaViewer, {timeout:30000});
    await page.waitForLoadState('networkidle');
    await page.evaluate(async data => { await window.testApp.loadGraphData(data); }, workflow);
    await page.locator('.director-tools-panorama-viewport').waitFor({state:'visible'});
    assert.equal(await page.locator('.director-tools-panorama-viewport').count(), 1);
    await page.evaluate(async () => { await window.testApp.queuePrompt(0,1); });
    await page.waitForFunction(() => document.querySelector('.director-tools-panorama-viewport [role="status"]')?.textContent.includes('2000 × 1000'), {timeout:30000});
    const initial = await page.evaluate(async () => (await window.testApp.graphToPrompt()).output['2'].inputs);
    assert.equal(initial.width,1920); assert.equal(initial.height,1080);
    assert.equal(initial.projection,'360 Panorama');
    assert.equal(initial.camera_height,0);
    assert.ok(await page.evaluate(()=>window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').outputs.some(output=>output.name==='prompt'&&output.type==='STRING')),'Legacy workflow exposes the appended STRING prompt output');
    await page.getByLabel('Yaw (degrees)').fill('35');
    await page.getByLabel('Yaw (degrees)').dispatchEvent('change');
    await page.getByLabel('Shot ID').fill('SH010');
    await page.getByLabel('Shot name',{exact:true}).selectOption('__custom__');
    await page.getByLabel('Custom shot name',{exact:true}).fill('Door');
    await page.getByRole('button',{name:'Save preset',exact:true}).click();
    await page.getByLabel('Yaw (degrees)').fill('-90');
    await page.getByLabel('Yaw (degrees)').dispatchEvent('change');
    await page.getByLabel('Saved shots').dispatchEvent('change');
    const named=await page.evaluate(async()=> (await window.testApp.graphToPrompt()).output['2'].inputs);
    assert.ok(Math.abs(named.center_x-(.5+35/360))<1e-8);
    assert.equal(named.projection,'360 Panorama');
    await page.getByRole('button',{name:'Reset framing',exact:true}).click();
    const canvas=page.getByRole('img',{name:/Camera viewport/});
    const b=await canvas.boundingBox();
    await page.mouse.move(b.x+b.width/2,b.y+b.height/2);
    await page.mouse.down();await page.mouse.move(b.x+b.width/2+40,b.y+b.height/2,{steps:5});await page.mouse.up();
    const graphScale=await page.evaluate(() => window.testApp.canvas.ds.scale);
    await page.mouse.wheel(0,-200);
    await page.waitForFunction(() => window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer')?.widgets.find(w=>w.name==='zoom').value>1);
    assert.equal(await page.evaluate(() => window.testApp.canvas.ds.scale),graphScale,'Viewport wheel also zoomed ComfyUI graph');
    const zoomedIn=await page.evaluate(() => window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').widgets.find(w=>w.name==='zoom').value);
    await page.mouse.wheel(0,100);
    await page.waitForFunction(previous => window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').widgets.find(w=>w.name==='zoom').value<previous,zoomedIn);
    assert.equal(await page.evaluate(() => window.testApp.canvas.ds.scale),graphScale,'Viewport wheel-out also zoomed ComfyUI graph');
    await page.evaluate(() => {
        const n=window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer');
        n.widgets.find(w=>w.name==='center_x').value=.001;
        n.widgets.find(w=>w.name==='zoom').value=1;
    });
    await canvas.press('ArrowLeft');
    assert.ok(await page.evaluate(() => window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').widgets.find(w=>w.name==='center_x').value>.9));
    // Place the final saved camera near the seam to exercise wrapping on output.
    await page.evaluate(() => {
        const w=window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').widgets.find(w=>w.name==='zoom');
        w.value=1.25;w.callback(w.value);
    });
    await page.evaluate(() => {
        const n=window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer');
        const w=n.widgets.find(w=>w.name==='camera_height');w.value=.4;w.callback(w.value);
    });
    await page.waitForFunction(() => document.querySelector('.director-tools-panorama-viewport [role="status"]')?.textContent.includes('Height +0.40'));
    const state = await page.evaluate(async () => {
        const data=await window.testApp.graphToPrompt();
        return {workflow:data.workflow,inputs:data.output['2'].inputs};
    });
    assert.equal(state.inputs.camera_height,.4);
    assert.ok(state.inputs.center_x > .9); assert.ok(state.inputs.zoom > 1);
    assert.equal('director_tools_panorama_viewport' in state.inputs, false);
    await page.evaluate(async data => { await window.testApp.loadGraphData(data); }, state.workflow);
    await page.waitForFunction(() => document.querySelector('.director-tools-panorama-viewport [role="status"]')?.textContent.includes('2000 × 1000'));
    const restored=await page.evaluate(async () => (await window.testApp.graphToPrompt()).output['2'].inputs);
    assert.deepEqual(restored,state.inputs);
    assert.equal(await page.evaluate(()=>window.testApp.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots.shots[0].shot_id),'SH010');
    await page.locator('.director-tools-panorama-viewport').screenshot({path:new URL('../docs/preview.png',import.meta.url).pathname});
    const viewerPrevious=Object.keys(await(await fetch(`${base}/history`)).json());
    await page.evaluate(async () => { await window.testApp.queuePrompt(0,1); });
    const viewerResult=await completedAfter(viewerPrevious,'DirectorToolsPanoramaViewer');
    assert.equal(viewerResult.status.status_str,'success');
    assert.ok(!errors.some(e=>e.includes('DirectorToolsPanoramaViewer') || e.includes('director_tools_panorama')),errors);
    console.log('Real ComfyUI browser passed: extension UI, source preview, pan/zoom, prompt inputs, workflow reload and execution.');
    const batchWorkflow=JSON.parse(await readFile(new URL('../example_workflows/director_tools_batch.json',import.meta.url)));
    await page.evaluate(async data=>window.testApp.loadGraphData(data),batchWorkflow);
    const batchInputs=await page.evaluate(async()=> (await window.testApp.graphToPrompt()).output['2'].inputs);
    assert.equal(JSON.parse(batchInputs.presets_json).shots.length,3);
    assert.equal(batchInputs.save_files,false);
    const previousIDs=Object.keys(await(await fetch(`${base}/history`)).json());
    await page.evaluate(async()=>window.testApp.queuePrompt(0,1));
    // Frontend queuing is asynchronous; an empty queue can precede submission.
    // Wait for this workflow's new history entry instead of reading the old run.
    const last=await completedAfter(previousIDs,'DirectorToolsBatchPanorama');
    assert.equal(last.status.status_str,'success');
    assert.equal(last.outputs['3'].images.length,3);
    assert.equal(last.outputs['4'].images.length,1);
    console.log('Real ComfyUI batch workflow imported and executed: three shots and one contact sheet.');
    if (errors.length) console.log('Unrelated host page errors:',errors);
} finally { await browser.close(); }
