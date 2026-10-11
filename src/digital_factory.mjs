import {ACTIONS,TYPES,makeWorld} from './worlds.mjs';
import {decide,evaluate,eligible} from './core.mjs';
const $=id=>document.getElementById(id);
let kind='machine',progress=0,selected='none',timer=null,hasApproval=true,fresh=true;
const labels={machine:'Máy cắt M-CUT-01 dừng hoạt động',material:'PART-X không đủ cho lô tiếp theo',quality:'LOT-101 đang chờ kiểm tra QA'};
const eventDetails={machine:'Máy cắt ngừng hoạt động → lắp ráp chờ đầu vào → QA lùi lịch → nguy cơ giao hàng trễ.',material:'Kho PART-X thiếu số lượng cần thiết → công đoạn cắt chờ cấp vật tư → toàn chuỗi bị dời.',quality:'LOT-101 bị giữ → chưa được qua cổng QA → ETA giao hàng bị lùi.'};
const display=n=>Number.isFinite(n)?n.toFixed(1)+'m':'—';
function getWorld(){return makeWorld(kind,{dataFresh:fresh,backupApproved:hasApproval,substituteApproved:hasApproval,qaExpediteApproved:hasApproval,backupCapacity:hasApproval?200:0},'digital-factory-'+kind)}
function calculate(){const w=getWorld();const recommendation=decide(w,'integrated');const at=recommendation.decisionAt;const base=evaluate(w,'none',at);const check=eligible(w,selected);const current=check.ok?evaluate(w,selected,at):base;return {w,recommendation,base,current,at};}
function update(){const active=progress>=33,affected=progress>=58,done=progress>=85;const {w,recommendation,base,current,at}=calculate();
 document.querySelectorAll('[data-scenario]').forEach(b=>b.classList.toggle('active',b.dataset.scenario===kind));
 $('tick').textContent='T+'+String(Math.round(progress*1.2)).padStart(2,'0');$('scrub').value=progress;
 $('phase').textContent=active?(done?'Phương án đang được đánh giá':affected?'Tác động lan truyền qua chuỗi':'Sự cố được phát hiện'):'Dây chuyền hoạt động bình thường';
 $('eventStatus').textContent=active?'EVENT: '+kind.toUpperCase():'EVENT: NOT INJECTED';
 $('incidentName').textContent=active?labels[kind]:'Chưa có sự cố';$('incidentDetail').textContent=active?eventDetails[kind]:'Chạy mô phỏng để đưa sự cố vào nhà máy.';
 $('stock').textContent=kind==='material'&&active?'PART-X · 60 units':'PART-X · 180 units';
 $('machineState').textContent=kind==='machine'&&active?'STOPPED · MAINTENANCE':'RUNNING';
 $('factory').classList.toggle('alert',active); document.querySelectorAll('.station').forEach(s=>s.classList.remove('error','impact'));
 if(active){const target={machine:'mes',material:'wms',quality:'tms'}[kind];document.querySelector(`[data-station="${target}"]`).classList.add('error');if(affected){document.querySelector('[data-station="tms"]').classList.add('impact');document.querySelector('[data-station="mes"]').classList.add('impact')}}
 for(const id of ['g-order','g-material','g-machine','g-ship'])$(id).classList.remove('hit','affected');
 if(active){$(kind==='machine'?'g-machine':kind==='material'?'g-material':'g-ship').classList.add('hit');if(affected){$('g-ship').classList.add('affected');if(kind!=='quality')$('g-machine').classList.add('affected')}}
 $('propagation').textContent=active?eventDetails[kind]:'Đơn hàng → vật tư → công đoạn → QA → giao hàng. Các liên kết được minh họa từ chuỗi trong engine.';
 $('shipping').textContent=active?`ETA ORD-101: ${display(current.rows[0].eta)}`:'ETA từ engine';
 $('eta101').textContent=active?display(current.rows[0].eta):'—';$('eta102').textContent=active?display(current.rows[1].eta):'—';
 $('late').textContent=active?display(current.lateMinutes):'—';$('loss').textContent=active?current.loss.toFixed(1):'—';
 $('recommended').textContent=recommendation.status==='VERIFY'?'Yêu cầu xác minh dữ liệu':recommendation.status==='ESCALATE'?'Chuyển người vận hành':ACTIONS[recommendation.chosen].name;
 $('why').textContent=recommendation.why;
 $('actions').innerHTML=TYPES[kind].actions.map(a=>{const valid=eligible(w,a);const result=valid.ok?evaluate(w,a,at):null;return `<button data-action="${a}" ${valid.ok?'':'disabled'} class="${selected===a?'active':''}"><span>${ACTIONS[a].name}</span><small>${result?'Loss '+result.loss.toFixed(1):'KHÔNG HỢP LỆ'}</small></button>`}).join('');
 document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.action;update()}));
 $('rows').innerHTML=active?current.rows.map((r,i)=>`<tr><td>${r.id}</td><td>${display(r.due)}</td><td>${display(base.rows[i].eta)}</td><td>${display(r.eta)}</td><td>${display(r.late)}</td></tr>`).join(''):'<tr><td colspan="5">Chạy mô phỏng để hiển thị dữ liệu tính từ engine.</td></tr>';
}
function stop(){clearInterval(timer);timer=null;$('play').textContent='▶ Chạy mô phỏng'}
function start(){if(timer){stop();return}if(progress>=100)progress=0;$('play').textContent='Ⅱ Tạm dừng';timer=setInterval(()=>{progress=Math.min(100,progress+2);update();if(progress===100)stop()},75)}
$('play').onclick=start;$('reset').onclick=()=>{stop();progress=0;selected='none';update()};$('scrub').oninput=e=>{stop();progress=Number(e.target.value);update()};
document.querySelectorAll('[data-scenario]').forEach(b=>b.onclick=()=>{stop();kind=b.dataset.scenario;selected='none';progress=0;update()});
$('authorized').onchange=e=>{hasApproval=e.target.checked;if(!eligible(getWorld(),selected).ok)selected='none';update()};$('fresh').onchange=e=>{fresh=e.target.checked;update()};
$('export').onclick=()=>{const result=calculate();const doc={disclaimer:'Synthetic rule-based digital factory simulation; not DENSO measured performance',scenario:kind,progress,chosenAction:selected,world:result.w,decision:result.recommendation,baseline:result.base,selected:result.current};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(doc,null,2)],{type:'application/json'}));a.download='factorypulse-digital-factory.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
update();
