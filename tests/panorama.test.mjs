import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cameraAngles, sphericalUV, panSphere } from '../web/lib/geometry.mjs';

test('spherical center rays hit cardinal panorama coordinates and seam wraps', () => {
    for (const u of [0,.25,.5,.75,1]) {
        const actual = sphericalUV(0,0,16/9,u,.5,1);
        assert.ok(Math.abs(actual.u - u%1) < 1e-8);
        assert.ok(Math.abs(actual.v - .5) < 1e-8);
    }
    assert.deepEqual(cameraAngles(0,.5,1),cameraAngles(1,.5,1));
});
test('perspective FOV, vertical direction and zoom follow the camera contract', () => {
    assert.ok(Math.abs(sphericalUV(0,-1,1,.5,.5,1).v - (.5-37.5/180)) < 1e-8);
    assert.ok(Math.abs(sphericalUV(0,1,1,.5,.5,1).v - (.5+37.5/180)) < 1e-8);
    assert.ok(Math.abs(sphericalUV(0,0,1,.5,.25,1).v-.25) < 1e-8);
    const expected=.5+Math.atan(Math.tan(37.5*Math.PI/180)*16/9)/(2*Math.PI);
    assert.ok(Math.abs(sphericalUV(1,0,16/9,.5,.5,1).u-expected)<1e-8);
    assert.ok(sphericalUV(1,0,16/9,.5,.5,2).u<expected);
});
test('sphere dragging crosses seam repeatedly and vertical camera remains bounded', () => {
    let p=panSphere(.01,.5,1,100,0,400,400,1);
    assert.ok(p.x>.9);
    for(let i=0;i<30;i++) { p=panSphere(p.x,p.y,1,500,0,400,400,1);assert.ok(p.x>=0&&p.x<1); }
    assert.ok(panSphere(.5,.5,1,0,10000,400,400,1).y>0);
});

test('height moves world origin vertically and zero keeps old rays', () => {
    for(const h of [-.8,-.4,0,.4,.8]) {
        const uv=sphericalUV(0,0,1,.5,.5,1,h);
        assert.ok(Math.abs(uv.v-(.5-Math.asin(h)/Math.PI))<1e-8);
        assert.ok(Math.abs(uv.u-.5)<1e-8);
    }
    assert.deepEqual(sphericalUV(.3,-.2,1.7,.8,.4,2,0),sphericalUV(.3,-.2,1.7,.8,.4,2));
});
