import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const $=id=>document.getElementById(id); const viewport=$('viewport');
const scene=new THREE.Scene();scene.background=new THREE.Color(0x081521);scene.fog=new THREE.Fog(0x081521,29,60);
const camera=new THREE.PerspectiveCamera(44,viewport.clientWidth/viewport.clientHeight,.1,110);camera.position.set(15.2,12.8,17.4);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(viewport.clientWidth,viewport.clientHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.5;viewport.prepend(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1.5,0);controls.enableDamping=true;controls.minDistance=9;controls.maxDistance=48;controls.maxPolarAngle=Math.PI*.49;
scene.add(new THREE.HemisphereLight(0xb6dfff,0x1e293b,3));const sun=new THREE.DirectionalLight(0xe5f7ff,4);sun.position.set(10,22,8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);scene.add(sun);
function box(w,h,d,color,x,y,z,metal=.35){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color,metalness:metal,roughness:.48}));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;scene.add(m);return m}
box(28,.2,19,0x203343,0,-.15,0);const grid=new THREE.GridHelper(28,28,0x31778a,0x1d3c4b);grid.position.y=0;scene.add(grid);
// True volumetric CNC enclosures, racks, articulated robots, conveyors and pallets.
const machines=[];
for(let i=0;i<3;i++){
 const x=-6+i*6.2;const base=box(3.7,3.2,3.1,0x8198a4,x,1.7,-3.6);box(2.4,1.7,.09,0x15334e,x,1.9,-2);box(1,.9,.1,0x67bbde,x+.9,2.2,-1.93);box(3.9,.2,3.3,0x304e5f,x,.15,-3.6);
 const signal=box(.15,.6,.15,0x26eac1,x+1.5,3.65,-3);machines.push({base,signal});
 for(let r=0;r<3;r++)box(.5,.16,.4,0xaab7c4,x-.75+r*.7,1.35,-1.82);
}
for(let i=0;i<4;i++){const z=-5+i*2.7;box(4,.18,.4,0xefb42e,-11,1.7,z);for(let j=0;j<4;j++)box(.75,.7,.65,0xb78c58,-12.1+j*.8,.95,z)}
const belts=[];for(let i=0;i<3;i++){const x=-6+i*6.2;box(4,.35,1,0x283f50,x,.55,1.2);for(let j=0;j<5;j++){const r=new THREE.Mesh(new THREE.CylinderGeometry(.12,.12,3.8,10),new THREE.MeshStandardMaterial({color:0x91a5b4,metalness:.8,roughness:.2}));r.rotation.z=Math.PI/2;r.position.set(x,.78,.7+j*.25);scene.add(r)}for(let j=0;j<3;j++){const part=box(.42,.26,.48,0x63e2e7,x-1.25+j*1.1,1.05,1.1);belts.push({part,x,offset:j*.33})}}
function robot(x,z){const root=new THREE.Group();root.position.set(x,.2,z);scene.add(root);const pedestal=new THREE.Mesh(new THREE.CylinderGeometry(.55,.7,.8,16),new THREE.MeshStandardMaterial({color:0xeba12d,metalness:.5}));root.add(pedestal);const a=new THREE.Group();a.position.y=.45;root.add(a);let arm=new THREE.Mesh(new THREE.BoxGeometry(.38,2.3,.48),new THREE.MeshStandardMaterial({color:0xffa41b,metalness:.4}));arm.position.y=1.1;arm.castShadow=true;a.add(arm);const b=new THREE.Group();b.position.y=2.25;a.add(b);arm=new THREE.Mesh(new THREE.BoxGeometry(.35,1.9,.44),new THREE.MeshStandardMaterial({color:0xf1aa2c,metalness:.5}));arm.position.y=.9;b.add(arm);const gripper=new THREE.Mesh(new THREE.BoxGeometry(.65,.2,.42),new THREE.MeshStandardMaterial({color:0x98c5d2}));gripper.position.y=1.95;b.add(gripper);return {a,b}}
const robots=[robot(-8,4.5),robot(0,4.5),robot(7,4.5)];
// Motion is a repeatable six-phase pick-and-place cycle, NOT the CP-SAT schedule.
// A payload must remain stationary until grip, then follow the end-effector, then remain at the drop target.
const cycleSeconds=9.6;
const pickDrop=[];
const cargoMat=new THREE.MeshStandardMaterial({color:0xe9bd65,roughness:.55,metalness:.15});
robots.forEach((r,i)=>{
 const rootX=[-8,0,7][i],rootZ=4.5;
 const incoming=box(1.06,.12,1.05,0x56718a,rootX-1.18,.35,rootZ);
 const outgoing=box(1.06,.12,1.05,0x387c78,rootX+1.18,.35,rootZ);
 const cargo=new THREE.Mesh(new THREE.BoxGeometry(.48,.42,.47),cargoMat.clone());scene.add(cargo);cargo.castShadow=true;
 const claw=new THREE.Group();claw.position.set(0,1.94,.0);r.b.add(claw);
 const metal=new THREE.MeshStandardMaterial({color:0xc2e3e6,metalness:.87,roughness:.2});
 const housing=new THREE.Mesh(new THREE.BoxGeometry(.6,.15,.55),metal);claw.add(housing);
 const jawL=new THREE.Mesh(new THREE.BoxGeometry(.08,.32,.12),metal);jawL.position.set(-.28,-.21,0);claw.add(jawL);
 const jawR=jawL.clone();jawR.position.x=.28;claw.add(jawR);
 const lamp=new THREE.PointLight(0x52e9d4,1.8,2);claw.add(lamp);
 pickDrop.push({r,i,rootX,rootZ,cargo,claw,jawL,jawR,prev:0,delivered:0});
});
const liveBadge=document.createElement('div');liveBadge.className='cycle-badge';liveBadge.setAttribute('aria-live','polite');liveBadge.textContent='ROBOT CELL · PICK / PLACE';viewport.append(liveBadge);
const lerp=(a,b,k)=>a+(b-a)*Math.max(0,Math.min(1,k));
const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function configureArm(r,x,y){
 // 2-DOF planar inverse kinematics. 0 points up; two segments of 2.25 and 1.95.
 const L1=2.25,L2=1.95;const X=x,Y=y-.65;
 const d=Math.min(L1+L2-.01,Math.max(Math.abs(L1-L2)+.02,Math.hypot(X,Y)));
 const cosine=Math.max(-1,Math.min(1,(d*d-L1*L1-L2*L2)/(2*L1*L2)));
 const elbow=Math.acos(cosine);
 const a=Math.atan2(Y,X)-Math.atan2(L2*Math.sin(elbow),L1+L2*Math.cos(elbow));
 r.a.rotation.z=a-Math.PI/2;r.b.rotation.z=elbow;
}
function animatePickDrop(t){
 let updates=0;
 for(const d of pickDrop){
  const phase=((t*.001+d.i*2.7)/cycleSeconds)%1;
  const prev=d.prev;if(phase<prev-.5)d.delivered++;
  d.prev=phase;
  const x0=-1.18,x1=1.18;let x=x0,y=2.45,grip=false,placed=false,stage='APPROACH';
  if(phase<.13){x=x0;y=lerp(2.45,1.06,smooth(phase/.13));stage='LOWER';}
  else if(phase<.20){x=x0;y=1.06;grip=phase>.155;stage='GRIP';}
  else if(phase<.33){x=x0;y=lerp(1.06,2.4,smooth((phase-.2)/.13));grip=true;stage='LIFT';}
  else if(phase<.57){x=lerp(x0,x1,smooth((phase-.33)/.24));y=2.4;grip=true;stage='TRANSFER';}
  else if(phase<.71){x=x1;y=lerp(2.4,1.06,smooth((phase-.57)/.14));grip=true;stage='PLACE';}
  else if(phase<.78){x=x1;y=1.06;grip=phase<.735;placed=!grip;stage='RELEASE';}
  else if(phase<.90){x=x1;y=lerp(1.06,2.45,smooth((phase-.78)/.12));placed=true;stage='RETRACT';}
  else{x=lerp(x1,x0,smooth((phase-.90)/.1));y=2.45;placed=true;stage='RETURN';}
  const halted=broken && disruption.includes('machine') && d.i===1;
  if(!halted){configureArm(d.r,x,y);d.claw.updateWorldMatrix(true,false);const tip=new THREE.Vector3();d.claw.getWorldPosition(tip);
    // Geometry: cargo y=.73 on the pallet; lift uses end effector as carrier.
    if(grip){d.cargo.position.set(tip.x,tip.y-.26,d.rootZ)}
    else if(placed){d.cargo.position.set(d.rootX+x1,.73,d.rootZ)}
    else{d.cargo.position.set(d.rootX+x0,.73,d.rootZ)}
    d.jawL.position.x=grip?-.25:-.36;d.jawR.position.x=grip?.25:.36;
    if(d.i===0)liveBadge.textContent='ROBOT CELL · '+stage+' · CYCLES '+d.delivered;
    updates++;
  }
 }
 if(!updates)liveBadge.textContent='ROBOT CELL · SAFETY STOP';
}

box(5,.4,2.4,0x384f66,7,.4,8);for(let x=4.5;x<10;x+=1)box(.6,.55,.8,0xd8a35a,x,1,8);
// Additional industrial geometry: modular robotic cell, safety fencing, warehouse stacks and logistics.
const iron=new THREE.MeshStandardMaterial({color:0x455c72,metalness:.76,roughness:.29});
const warningMat=new THREE.MeshStandardMaterial({color:0xffbd53,metalness:.52,roughness:.3});
function addPart(parent,geo,mat,x,y,z){const p=new THREE.Mesh(geo,mat);p.position.set(x,y,z);p.castShadow=true;p.receiveShadow=true;parent.add(p);return p;}
function frame(x,z,w,d){const g=new THREE.Group();g.position.set(x,0,z);scene.add(g);for(const px of [-w/2,w/2])for(const pz of [-d/2,d/2])addPart(g,new THREE.BoxGeometry(.09,2.2,.09),iron,px,1.1,pz);for(const zz of [-d/2,d/2]){addPart(g,new THREE.BoxGeometry(w,.11,.11),warningMat,0,2.18,zz);addPart(g,new THREE.BoxGeometry(w,.08,.08),iron,0,.75,zz)}return g;}
frame(-8,4.5,2.9,2.5);frame(0,4.5,2.9,2.5);frame(7,4.5,2.9,2.5);
for(let q=0;q<3;q++){let x=-6+q*6.2;box(3.6,.12,.22,0xd6e1e8,x,3.31,-2.06);box(.32,.5,.18,0x19283a,x-1.35,2.35,-1.89);box(.22,.08,.1,0x26dbe2,x-1.35,2.35,-1.81);const ch=box(2.8,.13,.6,0x617684,x,1,-1.8);ch.material.metalness=.88;for(const sx of [-1,1])box(.07,1.35,.07,0x8fd6e4,x+sx*1.8,1.8,-1.91)}
for(let i=0;i<7;i++){let x=-12+i*1.4;box(.85,.43,.92,i%2?0xc28e4f:0xb27c42,x,.32,7.1);box(.76,.06,.8,0x354657,x,.09,7.1)}
const agv=new THREE.Group();scene.add(agv);const agvBody=addPart(agv,new THREE.BoxGeometry(2.1,.32,1.2),new THREE.MeshStandardMaterial({color:0x37748f,metalness:.6,roughness:.3}),0,.38,0);addPart(agv,new THREE.BoxGeometry(1.45,.38,.95),warningMat,0,.7,0);for(let i of [-.68,.68])for(let j of [-.48,.48]){let wheel=addPart(agv,new THREE.CylinderGeometry(.2,.2,.12,14),iron,i,.2,j);wheel.rotation.x=Math.PI/2;}agv.position.set(-10,0,6);
const transportParts=[];for(let k=0;k<5;k++){const p=new THREE.Mesh(new THREE.BoxGeometry(.62,.34,.5),new THREE.MeshStandardMaterial({color:k%2?0xf4b94f:0x64d0d8,metalness:.3,roughness:.47}));scene.add(p);transportParts.push(p)}
// Bright overhead fixtures above the production corridor.
for(let x=-10;x<=10;x+=5){const light=new THREE.PointLight(0xd4ecff,13,10);light.position.set(x,7,0);scene.add(light);box(2,.08,.4,0xc9eaff,x,6.8,0)}

let disruption='machine';let broken=false;let current=null;
function updateMachines(){machines.forEach((m,i)=>{m.signal.material.color.setHex(broken&&disruption.includes('machine')&&i===1?0xff2b4e:0x25e4ad)});}
function animate(t){requestAnimationFrame(animate);controls.update();agv.position.x=-10+((t*.00085)%20);transportParts.forEach((p,k)=>{p.position.set(-9+((t*.001+k*2.4)%18),.94,1.2)});const run=!(broken&&disruption.includes('machine'));animatePickDrop(t);belts.forEach(({part,x,offset})=>{part.position.x=run?x+((t*.0006+offset)%3)-1.5:x});renderer.render(scene,camera)}requestAnimationFrame(animate);
new ResizeObserver(()=>{camera.aspect=viewport.clientWidth/viewport.clientHeight;camera.updateProjectionMatrix();renderer.setSize(viewport.clientWidth,viewport.clientHeight)}).observe(viewport);
$('scenario').addEventListener('change',()=>{disruption=$('scenario').value;updateMachines()});
$('run').addEventListener('click',async()=>{const button=$('run');button.disabled=true;$('feedback').textContent='Đang chạy CP-SAT thật...';disruption=$('scenario').value;broken=true;updateMachines();try{
 const input={instance:$('instance').value,scenario:disruption,seed:Number($('seed').value),focus:Number($('focus').value),timeout:Number($('timeout').value)};
 const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});current=await r.json();if(!r.ok)throw new Error(current.error);
 const td=s=>s===undefined?'—':String(s);$('results').replaceChildren();for(const [name,a] of Object.entries(current.arms)){const tr=document.createElement('tr');for(const v of [name,a.info.status,a.kpi?.focus_completion,a.kpi?.weighted_tardiness,a.kpi?.makespan]){const cell=document.createElement('td');cell.textContent=td(v);tr.append(cell)}$('results').append(tr)}
 $('finding').textContent=current.counterexample?'Đã tìm thấy phản ví dụ trên CP-SAT chính thức':'Chưa tìm thấy phản ví dụ theo điều kiện đang chọn';$('finding').className=current.counterexample?'good':'warn';
 const g=current.arms.C2.graph;if(g){const rules={};g.edges.forEach(e=>rules[e.rule]=(rules[e.rule]||0)+1);$('graph').replaceChildren();for(const [rule,count] of Object.entries(rules)){const d=document.createElement('p');d.textContent=`${rule}: ${count} cạnh`; $('graph').append(d)}}
 $('label').textContent=`${input.instance} • ${input.scenario} • ${current.counterexample?'LOCAL BACKFIRES':'NO VERIFIED BACKFIRE'} • JSON reproducible`; $('feedback').textContent='Solver hoàn thành. Bấm Xuất bằng chứng JSON.';$('export').disabled=false;
 }catch(e){$('feedback').textContent='Lỗi: '+e.message}finally{button.disabled=false}});
$('export').addEventListener('click',()=>{if(!current)return;const blob=new Blob([JSON.stringify(current,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='factorypulse_official_p0_p1.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});

async function syncInstances(){const msg=$('instanceStatus');try{const r=await fetch('/api/instances',{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);const data=await r.json();let ok=0;for(const option of $('instance').options){const available=!!data.instances[option.value]?.available;option.disabled=!available;if(available)ok++;else option.textContent=option.value+' · chưa tải'}if($('instance').selectedOptions[0]?.disabled){$('instance').value=Object.keys(data.instances).find(k=>data.instances[k].available)||'mk01'}msg.textContent=`${ok}/3 bộ dữ liệu có sẵn. ${ok<3?'Bấm nút TẢI MK02/MK03 bên dưới để tải dữ liệu công khai.':''}`;msg.className='instance-status'+(ok<3?' warning':'');$('run').disabled=ok===0;}catch(e){msg.className='instance-status warning';msg.textContent='Không kiểm tra được danh sách instance: '+e.message}}
syncInstances();

const fetchButton=$('fetchInstances');
if(fetchButton)fetchButton.addEventListener('click',async()=>{
 fetchButton.disabled=true;fetchButton.textContent='ĐANG TẢI MK02/MK03…';
 try{const r=await fetch('/api/fetch-instances',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
 const body=await r.json();if(!r.ok)throw Error(body.error||'Tải thất bại');
 $('feedback').textContent=body.message||'Đã tải dữ liệu. Đang kiểm tra…';
 await syncInstances();
 }catch(e){$('feedback').textContent='Không tải được: '+e.message;}
 finally{fetchButton.disabled=false;fetchButton.textContent='TẢI MK02 / MK03';}
});
