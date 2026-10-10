import fs from 'node:fs';
import {makeWorld} from '../src/worlds.mjs';
import {trial} from '../src/core.mjs';
const families=['machine','material','quality'];
const output=[];
const cases=[
 {name:'critical-urgent',due:[120,138],manualLookup:20,feedLag:3},
 {name:'neutral-relaxed',due:[250,280],manualLookup:20,feedLag:3},
 {name:'fast-manual',due:[122,155],manualLookup:0,feedLag:8},
 {name:'late-feed',due:[120,145],manualLookup:7,feedLag:35},
 {name:'tight-capacity',due:[126,154],backupCapacity:120,manualLookup:20,feedLag:3},
 {name:'missing-approval',due:[115,142],backupApproved:false,substituteApproved:false,qaExpediteApproved:false,manualLookup:20,feedLag:3},
 {name:'stale-data',due:[135,165],dataFresh:false,manualLookup:15,feedLag:5},
 {name:'distribution-shift',due:[113,130],cutRate:2.4,assemblyRate:1.65,qaHoldUntil:95,manualLookup:17,feedLag:8}
];
for(const type of families)for(const c of cases){const {name,...values}=c;const w=makeWorld(type,values,`${type}-${name}`);output.push(trial(w));}
const clean=output.filter(x=>x.integrated.status!=='VERIFY');
const statistics={count:output.length,groups:families.map(type=>({type,count:output.filter(x=>x.type===type).length})),
  integrationWins:clean.filter(x=>x.integrated.loss<x.manual.loss-0.0001).length,
  ties:clean.filter(x=>Math.abs(x.integrated.loss-x.manual.loss)<0.0001).length,
  manualWins:clean.filter(x=>x.integrated.loss>x.manual.loss+0.0001).length,
  verificationCases:output.filter(x=>x.integrated.status==='VERIFY').length,
  invalidActions:output.filter(x=>x.manual.violations || x.integrated.violations).length,
  notes:['Synthetic rule-based benchmark. Neither manualLookup nor feedLag is measured at DENSO.',
    'Fixtures are hand-authored stress families; do NOT infer statistical generalization or ROI.',
    'Both policies have identical action sets, evaluation rules and oracle; latency is the manipulated assumption.',
    'A separate evaluator module could strengthen independence; current oracle shares declared deterministic model.']};
const rows=output.map(x=>({case:x.id,incident:x.type,manual_action:x.manual.action,manual_decision_min:x.manual.decisionAt,manual_loss:x.manual.loss,
 integrated_status:x.integrated.status,integrated_action:x.integrated.action,integrated_decision_min:x.integrated.decisionAt,
 integrated_loss:x.integrated.loss,delta_loss:Number((x.manual.loss-x.integrated.loss).toFixed(2)),
 manual_regret:x.manual.regret,integrated_regret:x.integrated.regret,hard_violations:x.manual.violations+x.integrated.violations}));
fs.mkdirSync('evidence',{recursive:true});
fs.writeFileSync('evidence/trials.json',JSON.stringify({method:'synthetic paired policy comparison',statistics,trials:output},null,2));
fs.writeFileSync('evidence/trials.csv',[Object.keys(rows[0]).join(','),...rows.map(r=>Object.values(r).join(','))].join('\n')+'\n');
fs.writeFileSync('evidence/summary.json',JSON.stringify(statistics,null,2));
console.log(JSON.stringify(statistics,null,2));
