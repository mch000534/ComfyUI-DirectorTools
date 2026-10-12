import test from 'node:test';
import assert from 'node:assert/strict';
import * as presets from '../web/lib/presets.mjs';

test('camera degree controls round trip canonical framing including seam', () => {
    for (const [cx,cy,zoom] of [[.5,.5,.5],[.5,.5,1],[.73,.4,2.7],[0,.1,32]]) {
        const degrees = presets.framingDegrees(cx,cy,zoom);
        const back = presets.degreeFraming(degrees.yaw,degrees.pitch,degrees.vertical_fov);
        assert.ok(Math.abs(back.center_x-cx)<1e-10);
        assert.ok(Math.abs(back.center_y-cy)<1e-10);
        assert.ok(Math.abs(back.zoom-zoom)<1e-10);
    }
});
test('preset document rejects invalid and duplicate shots atomically', () => {
    const shot = {shot_id:'SH010',name:'Door',source_id:'room_A',yaw:35,pitch:-4,vertical_fov:58,width:320,height:180,aspect_ratio:'16:9',camera_height:0};
    assert.deepEqual(presets.parsePresets(JSON.stringify({schema_version:1,shots:[shot]})).shots,[shot]);
    for (const document of [{schema_version:2,shots:[shot]},{schema_version:1,shots:[]},{schema_version:1,shots:[shot,shot]},{schema_version:1,shots:[shot,{...shot,shot_id:'sh010'}]},{schema_version:1,shots:[{...shot,vertical_fov:120}]},{schema_version:1,shots:[{...shot,width:300}]},{schema_version:1,shots:[{...shot,yaw:null}]}]) {
        assert.throws(()=>presets.parsePresets(JSON.stringify(document)));
    }
    assert.throws(()=>presets.parsePresets(JSON.stringify({schema_version:1,shots:[{...shot,aspect_ratio:['16:9']}]})));
});

test('new preset IDs increment suffixes and skip occupied IDs',()=>{
    assert.equal(presets.nextShotID('SH009',[]),'SH010');
    assert.equal(presets.nextShotID('SH999',[]),'SH1000');
    assert.equal(presets.nextShotID('SH001',[{shot_id:'sh002'},{shot_id:'SH003'}]),'SH004');
    assert.equal(presets.nextShotID('Door',[]),'Door001');
    assert.equal(presets.nextShotID('',[]),'SH001');
    assert.equal(presets.nextShotID('SH9007199254740992',[]),'SH9007199254740993');
});

test('reset IDs follows list order and preserves all shot settings',()=>{
    const shots=[{shot_id:'SH020',name:'Door',yaw:35},{shot_id:'SH001',name:'Wide',yaw:-90}];
    const before=JSON.stringify(shots);
    assert.deepEqual(presets.renumberShots(shots),[{...shots[0],shot_id:'SH001'},{...shots[1],shot_id:'SH002'}]);
    assert.equal(JSON.stringify(shots),before);
    assert.deepEqual(presets.renumberShots([]),[]);
});
