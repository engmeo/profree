import test from 'node:test';import assert from 'node:assert/strict';import {DEFAULT,simulate,assess,trace,stress,searchParadox} from '../resilience_lab/lab.mjs';
test('no invented KPI: KPI derives from actual schedule',()=>{const r=simulate(DEFAULT,'A-first');assert.equal(r.globalKpi,r.rows.reduce((s,x)=>s+x.late*x.priority,0));assert.equal(r.localKpi,r.rows[0].cutEnd)});
test('paradox example genuine local improvement vs factory degradation',()=>{const a=assess(DEFAULT);assert.equal(a.paradox,true);assert.ok(a.local.localKpi<a.alternative.localKpi);assert.ok(a.local.globalKpi>a.alternative.globalKpi)});
test('trace graph has verifiable edges',()=>{const g=trace(DEFAULT,'A-first');assert.equal(g.edges.length,8);assert.equal(g.nodes.length,9);assert.ok(g.edges.every(x=>x.evidence&&x.rule))});
test('stress grid finite reproducible includes blocked material',()=>{const a=stress();const b=stress();assert.deepEqual(a,b);assert.equal(a.sampleCount,36);assert.ok(a.firstMaterialBlock)});
test('search finds real counterexample',()=>{const a=searchParadox();assert.equal(a.found,true);assert.equal(assess(a.config).paradox,true)});
test('bad action rejected',()=>assert.throws(()=>simulate(DEFAULT,'fake')));
test('bad input rejected',()=>assert.throws(()=>simulate({...DEFAULT,qa:-1},'A-first')));
test('simulation deterministic',()=>assert.deepEqual(simulate(DEFAULT,'A-first'),simulate(DEFAULT,'A-first')));
