// Fresh, isolated browser context against a running ComfyUI; never queues work.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile} from 'node:fs/promises';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const workflow=JSON.parse(await readFile(new URL('../example_workflows/director_tools_viewer_to_batch.json',import.meta.url)));
const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'chrome'});
try{
    const page=await browser.newPage({viewport:{width:1800,height:1200}});
    const modules=[];
    page.on('response',r=>{if(r.url().includes('/lib/shot_controls.mjs'))modules.push(r.url());});
    await page.goto(process.env.COMFY_TEST_URL||'http://127.0.0.1:8199');
    await page.waitForFunction(()=>window.app&&window.LiteGraph?.registered_node_types?.DirectorToolsPanoramaViewer);
    await page.waitForLoadState('networkidle');
    await page.evaluate(async data=>window.app.loadGraphData(data),workflow);
    const select=page.getByLabel('Saved shots');
    const expected=await page.evaluate(()=>window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots.shots);
    assert.ok(expected.length>=2);
    for(const shot of expected.slice(0,2)){
        await select.selectOption(shot.shot_id);
        await page.waitForFunction(s=>{
            const n=window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer');
            const w=k=>n.widgets.find(w=>w.name===k).value;
            return Math.abs(w('center_x')-(((s.yaw/360+.5)%1+1)%1))<1e-8&&Math.abs(w('center_y')-(.5-s.pitch/180))<1e-8&&['width','height','aspect_ratio','camera_height'].every(k=>w(k)===s[k]);
        },shot);
        assert.equal(await page.getByLabel('Shot ID',{exact:true}).inputValue(),shot.shot_id);
    }
    assert.equal(await page.getByRole('button',{name:'Apply preset',exact:true}).count(),0);
    const original=await page.evaluate(()=>JSON.stringify(window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots));
    await page.getByRole('button',{name:'Add preset',exact:true}).click();
    const added=await page.evaluate(()=>window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots.shots);
    assert.equal(added.length,expected.length+1);
    assert.deepEqual(added.slice(0,-1),JSON.parse(original).shots);
    assert.equal(await select.inputValue(),added.at(-1).shot_id);
    assert.equal(await page.getByLabel('Shot ID',{exact:true}).inputValue(),added.at(-1).shot_id);
    await page.getByLabel('Shot name',{exact:true}).selectOption('Close-up');
    await page.getByRole('button',{name:'Save preset',exact:true}).click();
    assert.equal(await page.evaluate(()=>window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots.shots.at(-1).name),'Close-up');
    assert.equal(await page.getByLabel('Custom shot name',{exact:true}).isVisible(),false);
    await page.getByLabel('Shot name',{exact:true}).selectOption('__custom__');
    await page.getByLabel('Custom shot name',{exact:true}).fill('窗邊逆光');
    await page.getByRole('button',{name:'Save preset',exact:true}).click();
    await select.selectOption(expected[0].shot_id);
    await select.selectOption(added.at(-1).shot_id);
    assert.equal(await page.getByLabel('Shot name',{exact:true}).inputValue(),'__custom__');
    assert.equal(await page.getByLabel('Custom shot name',{exact:true}).inputValue(),'窗邊逆光');
    const beforeReset=await page.evaluate(()=>{
        const n=window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer');
        return {shots:n.properties.director_tools_shots.shots,camera:n.widgets.filter(w=>['center_x','center_y','zoom','width','height','aspect_ratio','camera_height','projection'].includes(w.name)).map(w=>w.value)};
    });
    await page.getByRole('button',{name:'Reset Shot ID',exact:true}).click();
    const reset=await page.evaluate(()=>window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').properties.director_tools_shots.shots);
    assert.deepEqual(reset,beforeReset.shots.map((s,i)=>({...s,shot_id:`SH${String(i+1).padStart(3,'0')}`})));
    assert.equal(await select.inputValue(),reset.at(-1).shot_id);
    assert.equal(await page.getByLabel('Shot ID',{exact:true}).inputValue(),reset.at(-1).shot_id);
    assert.deepEqual(JSON.parse(await page.getByLabel('Preset JSON').inputValue()).shots,reset);
    assert.deepEqual(await page.evaluate(()=>window.app.graph.nodes.find(n=>n.type==='DirectorToolsPanoramaViewer').widgets.filter(w=>['center_x','center_y','zoom','width','height','aspect_ratio','camera_height','projection'].includes(w.name)).map(w=>w.value)),beforeReset.camera);
    assert.ok(modules.some(url=>url.endsWith('?v=0.8.2')),'Fresh ComfyUI loads versioned preset controls');
    console.log('Actual ComfyUI: automatic selection, Add, common/custom names and Reset Shot ID pass; versioned module loaded; no queued generation.');
}finally{await browser.close();}
