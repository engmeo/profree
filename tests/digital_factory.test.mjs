import test from 'node:test';import assert from 'node:assert/strict';
import {makeWorld,TYPES} from '../src/worlds.mjs';
import {decide,evaluate,eligible} from '../src/core.mjs';
for(const kind of ['machine','material','quality'])test(`digital-factory ${kind}: propagation schedule and actions`,()=>{
 const w=makeWorld(kind),base=evaluate(w,'none',w.feedLag),decision=decide(w,'integrated');
 assert.equal(base.feasible,true);assert.equal(base.rows.length,2);assert.ok(base.rows.every(r=>r.qaEnd<=r.eta));
 assert.ok(TYPES[kind].actions.includes(decision.chosen));for(const a of TYPES[kind].actions){if(eligible(w,a).ok)assert.equal(evaluate(w,a,w.feedLag).feasible,true)}
});
test('digital-factory rejects unsafe interventions',()=>{for(const kind of ['machine','material','quality']){const w=makeWorld(kind,{backupApproved:false,substituteApproved:false,qaExpediteApproved:false});const d=decide(w);assert.notEqual(d.status,'VERIFY');assert.ok(eligible(w,d.chosen).ok)}});
test('digital-factory flags stale feed, without making automatic recommendation',()=>{for(const kind of ['machine','material','quality']){const d=decide(makeWorld(kind,{dataFresh:false}));assert.equal(d.status,'VERIFY');assert.equal(d.chosen,'none')}});
