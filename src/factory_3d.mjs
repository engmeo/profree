import {simulation,impactNodes,INCIDENT_TEXT} from './factory_3d_logic.mjs';
import {ACTIONS} from './worlds.mjs';
const $=id=>document.getElementById(id);let scenario='machine',progress=0,action='none',approved=true,fresh=true,selected='mes',playing=null;
const view=$('viewport'),cam=$('camera'),world=$('world');let azimuth=-33,tilt=57,zoom=1;
function camera(){cam.style.transform=`rotateX(${tilt}deg) rotateZ(${azimuth}deg) scale(${zoom})`;}
camera();let down=null;
view.addEventListener('pointerdown',e=>{if(e.button!==0)return;down={x:e.clientX,y:e.clientY,az:azimuth,tilt};view.setPointerCapture(e.pointerId)});
view.addEventListener('pointermove',e=>{if(!down)return;azimuth=down.az+(e.clientX-down.x)*.32;tilt=Math.max(25,Math.min(78,down.tilt+(e.clientY-down.y)*.24));camera()});
view.addEventListener('pointerup',()=>down=null);view.addEventListener('pointercancel',()=>down=null);
view.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.48,Math.min(1.5,zoom*(e.deltaY>0?.91:1.09)));camera()},{passive:false});
view.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')azimuth-=8;else if(e.key==='ArrowRight')azimuth+=8;else if(e.key==='ArrowUp')tilt=Math.max(25,tilt-5);else if(e.key==='ArrowDown')tilt=Math.min(78,tilt+5);else if(e.key==='+')zoom=Math.min(1.5,zoom+.1);else if(e.key==='-')zoom=Math.max(.48,zoom-.1);else return;e.preventDefault();camera()});
$('resetCamera').onclick=()=>{azimuth=-33;tilt=57;zoom=1;camera()};
document.querySelectorAll('[data-node]').forEach(el=>el.onclick=()=>{selected=el.dataset.node;render()});
function stop(){if(playing!==null){clearInterval(playing);playing=null}$('play').textContent='▶ Chạy mô phỏng';world.classList.add('paused')}
function render(){const result=simulation(scenario,{approved,fresh,action});const active=progress>=33;const {hit,affected}=impactNodes(scenario,progress);
 document.querySelectorAll('[data-scenario]').forEach(b=>b.classList.toggle('active',b.dataset.scenario===scenario));
 document.querySelectorAll('[data-node]').forEach(el=>{el.classList.toggle('alert',active&&el.dataset.node===hit);el.classList.toggle('affected',active&&affected.includes(el.dataset.node));el.classList.toggle('selected',el.dataset.node===selected)});
 document.querySelectorAll('[data-graph]').forEach(el=>{el.classList.toggle('hit',active&&el.dataset.graph===hit);el.classList.toggle('impact',active&&affected.includes(el.dataset.graph))});
 world.classList.toggle('machine-stop',active&&scenario==='machine');world.classList.toggle('material-stop',active&&scenario==='material');world.classList.toggle('qa-stop',active&&scenario==='quality');
 const signal=$('signal');signal.classList.toggle('visible',active);signal.style.setProperty('--x',({machine:'6px',material:'-255px',quality:'266px'})[scenario]);signal.style.setProperty('--y',({machine:'-55px',material:'75px',quality:'-155px'})[scenario]);
 $('incidentBadge').textContent=active?'⚠ '+({machine:'MACHINE DOWN',material:'MATERIAL SHORTAGE',quality:'QA HOLD'})[scenario]:'● NORMAL · Dây chuyền đang chạy';$('clock').textContent='T+'+Math.round(progress*1.2);
 $('progress').value=progress;$('phase').textContent=progress<33?'Bình thường':progress<58?'Đã phát hiện sự cố':progress<85?'Đang lan truyền ảnh hưởng':'Đánh giá phương án';$('selectedNode').textContent=selected.toUpperCase();
 $('story').textContent=active?INCIDENT_TEXT[scenario]:'Máy móc và băng chuyền đang vận hành bình thường.';
 $('ripple').textContent=active?INCIDENT_TEXT[scenario]:'ERP → WMS → MES → QA → TMS. Các khâu dùng cùng dữ liệu kịch bản.';
 const show=n=>Number(n).toFixed(1)+' phút';$('eta1').textContent=active?show(result.current.rows[0].eta):'—';$('eta2').textContent=active?show(result.current.rows[1].eta):'—';$('late').textContent=active?show(result.current.lateMinutes):'—';$('loss').textContent=active?result.current.loss.toFixed(1):'—';
 $('comparison').textContent=active?`Không can thiệp: ${show(result.baseline.lateMinutes)} trễ | Đang chọn: ${show(result.current.lateMinutes)} trễ. Dùng cùng engine mô phỏng.`:'Chạy mô phỏng để tính lại ETA theo kịch bản.';
 $('recommendation').textContent=result.decision.status==='VERIFY'?'VERIFY: yêu cầu xác minh dữ liệu':result.decision.status==='ESCALATE'?'ESCALATE: cần người vận hành xử lý':result.decision.status==='NO_ACTION'?'NO ACTION: chưa có phương án tốt hơn đáng kể':`RECOMMEND: ${ACTIONS[result.decision.chosen].name}`;
 $('actionList').innerHTML=result.options.map(o=>`<button data-action="${o.key}" class="${action===o.key?'active':''}" ${o.valid.ok?'':'disabled'}><span>${o.label}</span><b>${o.outcome?'Loss '+o.outcome.loss.toFixed(1):'Không hợp lệ'}</b></button>`).join('');
 document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{action=b.dataset.action;render()});
}
$('play').onclick=()=>{if(playing!==null){stop();return}if(progress>=100)progress=0;world.classList.remove('paused');$('play').textContent='Ⅱ Tạm dừng';playing=setInterval(()=>{progress=Math.min(100,progress+2);render();if(progress===100)stop()},80)};
$('reset').onclick=()=>{stop();progress=0;action='none';render()};$('progress').oninput=e=>{stop();progress=+e.target.value;render()};
document.querySelectorAll('[data-scenario]').forEach(b=>b.onclick=()=>{stop();scenario=b.dataset.scenario;action='none';progress=0;render()});
$('approved').onchange=e=>{approved=e.target.checked;action='none';render()};$('fresh').onchange=e=>{fresh=e.target.checked;render()};
$('export').onclick=()=>{const result=simulation(scenario,{approved,fresh,action});const doc={notice:'Synthetic 3D visualizer; what-if projection from existing FactoryPulse rule engine. No real DENSO measurements.',progress,selectedNode:selected,...result};const blob=new Blob([JSON.stringify(doc,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='factorypulse-3d-trial.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
world.classList.add('paused');render();
