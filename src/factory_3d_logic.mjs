import {ACTIONS, TYPES, makeWorld} from './worlds.mjs';
import {decide,evaluate,eligible} from './core.mjs';
export const INCIDENT_TEXT={machine:'Máy cắt M-CUT-01 ngừng → công đoạn phía sau bị chậm → ETA giao hàng tăng.',material:'Kho PART-X thiếu vật tư → công đoạn cắt phải chờ lô nhập tiếp theo.',quality:'LOT-101 đang QA HOLD → chưa được phép giao khi chưa qua kiểm định.'};
export function simulation(scenario,{approved=true,fresh=true,action='none'}={}){
  const w=makeWorld(scenario,{backupApproved:approved,substituteApproved:approved,qaExpediteApproved:approved,backupCapacity:approved?200:0,dataFresh:fresh},'factory-3d-'+scenario);
  const decision=decide(w,'integrated');
  const actionValidity=eligible(w,action);
  const chosen=actionValidity.ok?action:'none';
  const baseline=evaluate(w,'none',decision.decisionAt);
  const current=evaluate(w,chosen,decision.decisionAt);
  const options=TYPES[scenario].actions.map(a=>({key:a,label:ACTIONS[a].name,valid:eligible(w,a),outcome:eligible(w,a).ok?evaluate(w,a,decision.decisionAt):null}));
  return {scenario,world:w,decision,baseline,current,options,chosen,actionValidity};
}
export function impactNodes(scenario,progress){
  if(progress<33)return {hit:null,affected:[]};
  const hit={machine:'mes',material:'wms',quality:'qa'}[scenario];
  const affected=progress>=58 ? ({machine:['qa','tms'],material:['mes','qa','tms'],quality:['tms']}[scenario]):[];
  return {hit,affected};
}
