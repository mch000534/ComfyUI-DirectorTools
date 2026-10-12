// Dedicated isolated host test for workflow properties -> STRING -> batch execution.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile} from 'node:fs/promises';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.COMFY_TEST_URL||'http://127.0.0.1:8199';
const workflow=JSON.parse(await readFile(new URL('../example_workflows/director_tools_viewer_to_batch.json',import.meta.url)));
const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'chrome'});
try{
    const page=await browser.newPage({viewport:{width:1800,height:1200}});
    await page.goto(base);
    await page.waitForFunction(()=>window.app&&window.LiteGraph?.registered_node_types?.DirectorToolsPanoramaViewer);
    await page.waitForLoadState('networkidle');
    await page.evaluate(async data=>window.app.loadGraphData(data),workflow);
    await page.getByLabel('Yaw (degrees)').fill('-20');
    await page.getByLabel('Yaw (degrees)').dispatchEvent('change');
    await page.getByRole('button',{name:'Save preset',exact:true}).click();
    const state=await page.evaluate(async()=>{
        const preview=window.LiteGraph.createNode('PreviewAny');
        window.app.graph.add(preview);
        window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').connect(2,preview,0);
        const output=(await window.app.graphToPrompt()).output;
        return {output,consumerID:String(preview.id)};
    });
    assert.deepEqual(state.output['3'].inputs.presets_json,['2',2]);
    assert.deepEqual(state.output['3'].inputs.image,['1',0]);
    const previous=Object.keys(await(await fetch(`${base}/history`)).json());
    await page.evaluate(async()=>window.app.queuePrompt(0,1));
    const deadline=Date.now()+30000;
    let completed;
    while(Date.now()<deadline){
        const h=await(await fetch(`${base}/history`,{cache:'no-store'})).json();
        completed=Object.entries(h).find(([id,entry])=>!previous.includes(id)&&entry.prompt[2]['2']?.class_type==='DirectorToolsPanoramaViewer'&&entry.prompt[2]['3']?.class_type==='DirectorToolsBatchPanorama')?.[1];
        if(completed)break;
        await new Promise(r=>setTimeout(r,100));
    }
    assert.ok(completed,'Connected viewer/batch completed');
    assert.equal(completed.status.status_str,'success');
    const presets=JSON.parse(completed.outputs[state.consumerID].text[0]);
    assert.equal(presets.shots.length,3);
    assert.ok(Math.abs(presets.shots[0].yaw+20)<1e-8);
    assert.equal(completed.outputs['4'].images.length,3);
    assert.equal(completed.outputs['5'].images.length,1);
    console.log('Viewer presets_json: latest saved UI presets passed directly through STRING to Batch Panorama, producing three shots and one sheet.');
}finally{await browser.close();}
