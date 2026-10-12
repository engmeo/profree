import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
const root=resolve(import.meta.dirname,'..');
const hub=readFileSync(join(root,'demo_hub.html'),'utf8');
const hrefs=[...hub.matchAll(/href="([^"]+)"/g)].map(x=>x[1]).filter(x=>!x.startsWith('#'));
test('Demo Hub links all resolve locally',()=>{
  for(const href of hrefs){const clean=href.split('#')[0].split('?')[0];assert.ok(!clean.includes('://'));assert.ok(existsSync(resolve(root,clean)),`Broken local link: ${href}`)}
});
test('All five entrypoints are documented',()=>{
 for(const path of ['index.html','digital_factory.html','factory_3d.html','resilience_lab/index.html','factorypulse_experiment_v1/official_lab/web/index.html'])assert.ok(hub.includes(path),path);
});
test('Honest architecture disclosure is visible',()=>{
 assert.match(hub,/không tự chạy khi bấm nút/);assert.match(hub,/dữ liệu giả lập/);
});
