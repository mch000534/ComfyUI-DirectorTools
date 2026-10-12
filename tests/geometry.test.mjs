import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { cropRect, syncedSize, RATIOS, panCenter } from '../web/lib/geometry.mjs';

test('crop rectangles match shared Python contract', () => {
    const cases = JSON.parse(readFileSync(new URL('./geometry_cases.json', import.meta.url)));
    for (const c of cases) {
        const r = cropRect(...c.input);
        [r.x, r.y, r.width, r.height].forEach((v, i) => assert.ok(Math.abs(v - c.expected[i]) < 1e-8));
    }
});
test('all ratios keep a crop inside source at extreme centers and zoom', () => {
    for (const ratio of Object.values(RATIOS)) for (const zoom of [1, 1.2, 32]) {
        const r = cropRect(2011, 997, ratio, 1, 0, zoom);
        assert.ok(r.x >= 0 && r.y >= 0 && r.x + r.width <= 2011 + 1e-8);
        assert.ok(r.y + r.height <= 997 + 1e-8);
        assert.ok(Math.abs(r.width / r.height - ratio) < 1e-8);
    }
});
test('ratio synchronization honors last edited dimension and bounds', () => {
    assert.deepEqual(syncedSize('16:9', 1920, 100, 'width'), [1920, 1080]);
    assert.deepEqual(syncedSize('9:16', 100, 1080, 'height'), [608, 1080]);
    assert.deepEqual(syncedSize('Free', 777, 301, 'width'), [777, 301]);
    assert.deepEqual(syncedSize('16:9', 8192, 8192, 'height'), [8192, 4608]);
});
test('dragging image right moves camera left and clamps at edge', () => {
    const rect = cropRect(2000, 1000, 1, .5, .5, 1);
    const p = panCenter(rect, 2000, 1000, 100, 0, 500, 500);
    assert.equal(p.x, .4);
    assert.equal(p.y, .5);
    assert.equal(panCenter(rect, 2000, 1000, 99999, 0, 500, 500).x, .25);
});
