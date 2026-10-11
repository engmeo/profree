import test from 'node:test';import assert from 'node:assert/strict';import {simulation,impactNodes} from '../src/factory_3d_logic.mjs';
for(const type of ['machine','material','quality']){
 test('3D engine responds to '+type,()=>{const r=simulation(type);assert.equal(r.scenario,type);assert.equal(r.baseline.feasible,true);assert.equal(r.current.rows.length,2);assert.ok(r.options.length>=2)});
 test('3D graph propagation '+type,()=>{assert.equal(impactNodes(type,0).hit,null);assert.ok(impactNodes(type,65).affected.length>0)});
}
test('3D unsafe option never applied',()=>{const r=simulation('machine',{approved:false,action:'reroute'});assert.equal(r.chosen,'none');assert.equal(r.actionValidity.ok,false)});
test('3D stale input leads to verification',()=>{assert.equal(simulation('material',{fresh:false}).decision.status,'VERIFY')});
test('3D what-if uses same model as no intervention',()=>{const r=simulation('quality',{action:'none'});assert.equal(r.baseline.loss,r.current.loss)});
