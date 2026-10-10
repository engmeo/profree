// All fixtures are SYNTHETIC. No personal, DENSO, ERP or proprietary production data.
export const BASE = Object.freeze({
  quantities:[90,70], priorities:[2,1], due:[135,165], transit:18,
  cutRate:3, assemblyRate:2, inspectRate:4, stock:180,
  downtimeEnd:0, refillAt:0, qaHoldUntil:0,
  backupRate:2, backupCapacity:200, backupApproved:true,
  substituteApproved:true, substituteUnits:160, qaExpediteApproved:true,
  repairDuration:30, routeSetup:12, inboundDuration:38, qaReinspectDuration:28,
  decisionDeadline:60, // maximum time to make initial safe recommendation
  feedLag:3, manualLookup:15, // assumed time until trustworthy cross-department information arrives
  dataFresh:true,
});
export const TYPES={
  machine:{name:'Machine downtime',trigger:'MES · M-CUT-01',reason:'M-CUT-01 is unavailable; order queue is affected.',actions:['none','repair','reroute']},
  material:{name:'Material shortage',trigger:'WMS · PART-X',reason:'PART-X cannot cover the next full lot.',actions:['none','expedite','substitute']},
  quality:{name:'Quality hold',trigger:'QA · LOT-101',reason:'The first lot is held pending controlled inspection.',actions:['none','reinspect']},
};
export const ACTIONS={
  none:{name:'Wait / retain current plan',dept:'Planning',cost:0},
  repair:{name:'Expedite maintenance',dept:'Maintenance',cost:18},
  reroute:{name:'Route to approved backup',dept:'Production',cost:25},
  expedite:{name:'Expedite inbound shipment',dept:'Purchasing',cost:24},
  substitute:{name:'Use QA-approved substitute',dept:'Quality',cost:34},
  reinspect:{name:'Approved parallel reinspection',dept:'Quality',cost:17}
};
export function makeWorld(type,overrides={},id='illustration'){
  if(!TYPES[type])throw new Error('Unknown incident');
  return { ...BASE,
    ...(type==='machine'?{downtimeEnd:75}:type==='material'?{stock:60,refillAt:95}:{qaHoldUntil:165}),
    ...overrides,
    type,id
  };
}
export const DEMOS=[
  makeWorld('machine',{},'demo-machine'),
  makeWorld('material',{},'demo-material'),
  makeWorld('quality',{},'demo-quality'),
  makeWorld('machine',{backupApproved:false,qaExpediteApproved:false},'unsafe-backup'),
  makeWorld('material',{dataFresh:false},'stale-data'),
  makeWorld('quality',{qaExpediteApproved:false},'qa-approval-missing')
];
