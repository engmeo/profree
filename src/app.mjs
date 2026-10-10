import {ACTIONS,TYPES,makeWorld} from './worlds.mjs';
import {trial,decide,evaluate,oracle} from './core.mjs';
const $=id=>document.getElementById(id),n=x=>Number(x).toFixed(1);
let chosen='machine',fixture='normal',manualLookup=15,feedLag=3;
const effects={normal:{},fastManual:{manualLookup:0,feedLag:9},stale:{dataFresh:false},noApproval:{backupApproved:false,substituteApproved:false,qaExpediteApproved:false,backupCapacity:0},neutral:{due:[270,305]}};
const departments={machine:[['Maintenance','Verify outage and repair window.'],['Planning','Check impacted orders and replanning conditions.'],['Production','Authorize backup routing only if rated capacity permits.'],['Logistics','Escalate delivery risks.']],material:[['Warehouse','Confirm PART-X available balance and replenishment time.'],['Purchasing','Verify inbound shipment acceleration cost.'],['Quality','Approve any substitute part and required checks.'],['Planning','Refresh order commitment only after validation.']],quality:[['Quality','Retain hold; authorize controlled reinspection if acceptable.'],['Production','Isolate affected lot and preserve genealogy.'],['Planning','Recompute order-level ETA with the release gate.'],['Logistics','Prevent shipment until approval is documented.']]};
function world(){return makeWorld(chosen,{...effects[fixture],manualLookup,feedLag},'interactive-'+chosen+'-'+fixture)}
function actionName(a){return ACTIONS[a]?.name??a}
function render(){
 $('scenarioList').innerHTML=Object.entries(TYPES).map(([id,v])=>`<button data-type="${id}" class="${chosen===id?'selected':''}"><b>${v.name}</b><small>${v.trigger}</small></button>`).join('');
 document.querySelectorAll('[data-type]').forEach(b=>b.onclick=()=>{chosen=b.dataset.type;render()});
 $('manualLabel').textContent=manualLookup+' min';$('feedLabel').textContent=feedLag+' min';
 const w=world(),t=trial(w),s=decide(w,'manual'),f=decide(w,'integrated');
 $('eventTitle').textContent=TYPES[chosen].trigger+' · INJECTED EVENT';$('eventDesc').textContent=TYPES[chosen].reason;
 $('manualLoss').textContent=n(t.manual.loss);$('feedLoss').textContent=n(t.integrated.loss);
 const delta=t.manual.decisionAt-t.integrated.decisionAt;
 $('decisionDelta').textContent=(delta>=0?'+':'')+n(delta)+'m';$('decisionState').textContent=t.integrated.status;
 $('manualAction').textContent=actionName(t.manual.action);$('integratedAction').textContent=f.status==='VERIFY'?'Request human verification':f.status==='ESCALATE'?'Escalate to operator':actionName(t.integrated.action);
 $('manualWhy').textContent=s.why;$('integratedWhy').textContent=f.why;
 $('manualStats').textContent=`Decision: ${n(t.manual.decisionAt)} min · Regret: ${n(t.manual.regret)}`;
 $('integratedStats').textContent=`Decision: ${n(t.integrated.decisionAt)} min · Regret: ${n(t.integrated.regret)}`;
 $('orderTable').innerHTML=s.simulation.rows.map((r,i)=>{let u=f.simulation.rows[i];return `<tr><td>${r.id}</td><td>${n(r.due)}m</td><td>${n(r.eta)}m</td><td>${n(u.eta)}m</td><td>${n(u.late)}m</td></tr>`}).join('');
 const d=t.manual.loss-t.integrated.loss;
 const classif=f.status==='VERIFY'?'NEEDS VERIFICATION':(Math.abs(d)<0.001?'TIE':d>0?'INTEGRATION BENEFIT':'MANUAL SOP BETTER');
 $('resultClass').textContent=classif;
 $('resultText').textContent=f.status==='VERIFY'?'Stale information: no automatic recommendation.':(Math.abs(d)<.001?'No measured difference under this synthetic world.':d>0?`Integrated feed yields ${n(d)} fewer loss points.`:`Manual SOP yields ${n(-d)} fewer loss points.`);
 $('handoff').innerHTML=departments[chosen].map(([a,b])=>`<div class="handoff"><b>${a}</b><small>${b}</small></div>`).join('');
 $('download').onclick=()=>{const blob=new Blob([JSON.stringify({disclaimer:'Synthetic trial only; not validated DENSO ROI.',trial:t},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='factorypulse-trial.json';a.click();URL.revokeObjectURL(url)};
}
$('fixture').onchange=e=>{fixture=e.target.value;const x=effects[fixture];manualLookup=x.manualLookup??15;feedLag=x.feedLag??3;$('manual').value=manualLookup;$('feed').value=feedLag;render()};
$('manual').oninput=e=>{manualLookup=+e.target.value;render()};$('feed').oninput=e=>{feedLag=+e.target.value;render()};
fetch('./evidence/summary.json').then(r=>r.json()).then(x=>{for(const [id,key] of [['wins','integrationWins'],['ties','ties'],['losses','manualWins'],['verifies','verificationCases']])$(id).textContent=x[key]}).catch(()=>{for(const id of ['wins','ties','losses','verifies'])$(id).textContent='–'});
render();window.FactoryPulse={setIncident:(x)=>{chosen=x;render()},setFixture:(x)=>{fixture=x;manualLookup=effects[x].manualLookup??15;feedLag=effects[x].feedLag??3;$('fixture').value=x;$('manual').value=manualLookup;$('feed').value=feedLag;render()},getCurrent:()=>trial(world())};
