const path=require('node:path');
const pptxgen=require('pptxgenjs');const p=new pptxgen();p.layout='LAYOUT_WIDE';p.author='FactoryPulse | D3 Evidence';p.subject='DENSO Factory Hacks 2026 · D3';p.title='FactoryPulse D3: traceable incident decisions';p.lang='vi-VN';
const R=path.resolve(__dirname,'..'),W=13.333333,H=7.5,FG='Noto Sans';
const nav='143053',ink='192C3C',green='007D6A',muted='647587',blue='235184',red='9B3B44',lt='EDF7F5',amber='8C5B2D';
function slide(n){const s=p.addSlide();s.background={color:'FFFFFF'};s.addImage({path:path.join(R,'assets','template-bg',`p${n}.png`),x:0,y:0,w:W,h:H});return s;}
function text(s,str,x,y,w,h,size=13,bold=false,color=ink,opt={}){s.addText(str,{x,y,w,h,fontFace:FG,fontSize:size,bold,color,margin:0,breakLine:false,vertAlign:'mid',...opt});}
function box(s,x,y,w,h,color='F5F9FB',stroke='C8DFE0'){s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:.10,line:{color:stroke,width:.8},fill:{color},radius:.10})}
function note(s,title,body,x,y,w,h,accent=green){box(s,x,y,w,h);s.addShape(p.ShapeType.rect,{x:x+.16,y:y+.17,w:.055,h:.28,fill:{color:accent},line:{color:accent}});text(s,title,x+.28,y+.12,w-.47,.36,13.2,true,nav);text(s,body,x+.28,y+.58,w-.48,h-.65,11.3,false,ink,{valign:'top',breakLine:false})}
// 1 OFFICIAL COVER
{let s=slide(1);box(s,.65,5.55,7.04,1.05,'0E2745','2F6582');text(s,'FACTORYPULSE | CHALLENGE D3',.9,5.70,6.48,.31,21,true,'FFFFFF');text(s,'A traceable decision layer for production incidents',.9,6.12,6.5,.25,11.5,false,'ABF9E2');}
// 2 OFFICIAL SIX-QUESTION CHECKLIST
{let s=slide(2);text(s,'D3 — FACTORYPULSE / Incident-to-Order Decision Support',1.75,1.15,11.2,.26,13.2,true,blue);text(s,'✓',5.2,1.88,.25,.26,16,true,green);
 const rows=[
 'Khác biệt đề xuất: liên hệ sự cố → đơn hàng → lựa chọn có ràng buộc; có thể trả lời KHÔNG CAN THIỆP. Chưa chứng minh ưu thế thương mại.',
 'D3: kiểm tra giả thuyết rằng thông tin MES/WMS/QA và ERP chưa được khai thác đủ để hỗ trợ quyết định đúng lúc. Cần DENSO xác nhận.',
 '48 giờ: web demo + 17 test + 24 ca stress. 12 tuần pilot: mapping dữ liệu, replay sự cố, shadow mode, quyết định go/no-go.',
 'Thử nghiệm SYNTHETIC: 5 thắng / 14 hòa / 2 thua / 3 VERIFY; không có ROI thực. Nguy cơ dữ liệu cũ được công bố.',
 'Tích hợp đọc ERP/MES/WMS/QA/TMS, pilot 1 line rồi mở rộng; chỉ tăng quy mô nếu có ID liên kết và quyền phê duyệt rõ.',
 'Code và test có trên GitHub; thông tin thành viên và kinh nghiệm thực tế cần đội điền trước nộp (không tự tạo).'
 ];
 const y=[2.97,3.45,3.89,4.34,4.80,5.34],h=[.40,.40,.38,.42,.46,.42];
 rows.forEach((v,i)=>text(s,v,6.46,y[i],6.00,h[i],9.5,false,ink,{valign:'mid',breakLine:false}));
 box(s,.44,6.86,12.39,.38,'0B3652','0B3652');text(s,'Nếu được chọn, nhóm kiểm chứng lợi ích ra quyết định an toàn so với SOP trên một dây chuyền thí điểm.',.56,6.92,12.00,.27,10.3,true,'FFFFFF');}
// 3 TEAM
{let s=slide(3);text(s,'ĐỘI THI / CẦN BỔ SUNG THÔNG TIN ĐƯỢC XÁC NHẬN',.65,1.42,11.85,.45,18.5,true,nav);
 const roles=[['Factory problem / KPI','Tên: __________________','Pain point · quy trình · baseline'],['Data / Integration','Tên: __________________','ERP/MES/WMS schema · quality'],['Simulation / Testing','Tên: __________________','Engine · ràng buộc · kiểm thử'],['Web / Demo','Tên: __________________','Giao diện · video · triển khai'],['Product / Pitch','Tên: __________________','Slide · ROI assumptions · phản biện']];
 roles.forEach((r,i)=>{const x=.64+(i%3)*4.19,y=2.05+Math.floor(i/3)*1.65;box(s,x,y,3.97,1.41,'F3F9F8');text(s,r[0],x+.18,y+.15,3.55,.34,13,true,green);text(s,r[1],x+.18,y+.57,3.51,.26,11.2,false,nav);text(s,r[2],x+.18,y+.95,3.5,.25,10.4,false,muted);});
 box(s,.66,5.53,12.0,.55,'FFF7EF','E9CBA3');text(s,'Điền CV, LinkedIn/GitHub và kinh nghiệm thật của từng thành viên — không dùng ví dụ minh họa làm hồ sơ năng lực.',.87,5.64,11.58,.3,12.1,true,amber);}
// 4 PAIN
{let s=slide(4);text(s,'VẤN ĐỀ THỰC TẾ: THÔNG TIN ĐÃ CÓ, QUYẾT ĐỊNH CÓ ĐỦ NHANH?',.61,1.43,12.1,.49,18.5,true,nav);
 note(s,'1 · DENSO CÓ NỀN TẢNG SỐ', 'Bài báo JMA 06/2026 mô tả Future Command Room tổng hợp dữ liệu tồn kho và công suất line. Vì vậy, chúng tôi KHÔNG tuyên bố nhà máy chưa có dashboard.',.65,2.04,5.9,2.14,blue);
 note(s,'2 · KHOẢNG TRỐNG CẦN KIỂM CHỨNG', 'Một sự cố máy có thể ảnh hưởng tới lô, QA, đơn hàng và lịch giao. Chúng tôi kiểm tra liệu lớp hỗ trợ quyết định có cải thiện tốc độ, độ an toàn và truy vết so với SOP hiện hữu hay không.',6.78,2.04,5.9,2.14,green);
 box(s,.65,4.45,12.03,1.20,'ECF6F5','AAD8D1');text(s,'PAIN HYPOTHESIS ≠ FACTORY MEASUREMENT',.93,4.61,11.48,.28,15.5,true,nav);
 text(s,'Chưa có số liệu DENSO về thời gian điều phối liên bộ phận, tần suất sự cố, dữ liệu trễ hoặc chi phí thực. Pilot phải xác minh trước khi tính ROI.',.93,5.05,11.45,.36,11.5,false,ink);
 text(s,'Nguồn: JMA, 06/2026 — imd.jma.or.jp/management/report/activity_report41.html',.79,5.90,11.5,.24,10.4,false,muted);}
// 5 SOLUTION
{let s=slide(5);text(s,'GIẢI PHÁP — KHÔNG THAY THẾ COMMAND ROOM, BỔ SUNG QUYẾT ĐỊNH',.61,1.43,12.1,.44,18.7,true,nav);
 const st=[['01','READ','ERP / MES / WMS / QA / TMS'],['02','TRACE','Event → Process → Order'],['03','CHECK','Quality · Capacity · Permission'],['04','COMPARE','SOP Manual ↔ Integrated']];
 st.forEach((v,i)=>{const x=.65+i*3.15;box(s,x,2.10,2.93,1.20,i%2?'EDF6F9':'ECF8F5');text(s,v[0],x+.16,2.25,.52,.28,14.2,true,green);text(s,v[1],x+.71,2.22,1.98,.34,14.6,true,nav);text(s,v[2],x+.18,2.77,2.59,.31,10.35,false,ink,{align:'center'});});
 s.addImage({path:path.join(R,'assets','dashboard_preview.jpg'),x:.70,y:3.60,w:6.6,h:2.05});
 note(s,'ĐẦU RA HỖ TRỢ QUYẾT ĐỊNH','• ETA trễ theo từng đơn hàng\n• So sánh hành động đủ điều kiện\n• Báo VERIFY nếu data cũ\n• Hướng dẫn phê duyệt theo bộ phận',7.52,3.62,5.15,2.06,green);
 text(s,'SYNTHETIC / DETERMINISTIC — KHÔNG PHẢI AI SUY LUẬN NGUYÊN NHÂN TỪ DỮ LIỆU THẬT',.80,5.87,11.73,.31,11.7,true,red,{align:'center'});}
// 6 EFFECT / FINANCE
{let s=slide(6);text(s,'HIỆU QUẢ: CHẤM CẢ THẮNG, HÒA, THUA VÀ PHẢI XÁC MINH',.62,1.41,12,.46,18.2,true,nav);
 const bars=[['THẮNG',5,'279F89'],['HÒA',14,'8BA4B3'],['THUA',2,'C56B76'],['VERIFY',3,'D5A45A']];
 const startX=.77,startY=2.29,scale=.30;bars.forEach((v,i)=>{let yy=startY+i*.66;text(s,v[0],startX,yy,1.25,.26,12.2,true,nav);s.addShape(p.ShapeType.rect,{x:2.09,y:yy+.03,w:v[1]*scale,h:.26,fill:{color:v[2]},line:{color:v[2]}});text(s,String(v[1]),2.25+v[1]*scale,yy,1,.29,12.5,true,nav);});
 text(s,'24 CA / 3 LOẠI SỰ CỐ / DỮ LIỆU DO ĐỘI TẠO',.75,5.15,7.2,.28,11.7,true,green);
 box(s,7.62,2.09,5.05,3.31,'EEF6F7','B3D8D5');text(s,'CHI PHÍ / ROI: KHÔNG BỊA RA SỐ THỰC',7.86,2.27,4.56,.44,14.5,true,nav);
 text(s,'Cần đo: chi phí tích hợp + vận hành, phút xử lý sự cố, nhân lực, tần suất, chi phí hành động và tổn thất thực tránh được.',7.87,2.86,4.5,.87,11.4,false,ink,{valign:'top'});
 text(s,'Minh họa độ nhạy (giả định):',7.87,3.80,4.4,.26,11.6,true,green);
 text(s,'Đầu tư 50 triệu; lợi ích 5 triệu/tháng; vận hành 2 triệu/tháng ⇒ hoàn vốn 16,7 tháng. KHÔNG phải dự báo DENSO.',7.87,4.20,4.48,.92,11.3,false,ink,{valign:'top'});
 box(s,.71,5.61,11.97,.49,'FFF2F0','E6AFAA');text(s,'KẾT QUẢ BẤT LỢI: Mean loss của tích hợp CAO HƠN SOP trên 24 ca do feed cũ → cần cơ chế fallback/verification.',.91,5.7,11.55,.31,10.9,true,red);}
// 7 TIMELINE
{let s=slide(7);text(s,'THỜI GIAN: MINIMUM PROOF TRƯỚC, PILOT SAU',.65,1.42,12,.44,19.5,true,nav);
 const short=[['0–8h','Freeze claim · schema · SOP giả định'],['8–18h','17 test · 24 ca · cả kết quả âm tính'],['18–30h','Dashboard · trace → order · verify'],['30–40h','Video 2–3 phút · repo public'],['40–48h','Red-team 6 điều · nộp trước hạn']];
 short.forEach((v,i)=>{let y=2.08+i*.61;box(s,.68,y,5.97,.48,i%2?'F7FAFB':'EEF7F5');text(s,v[0],.89,y+.08,1.06,.28,11.2,true,green);text(s,v[1],2.10,y+.08,4.31,.26,10.9,false,ink);});
 const pilot=[['W1–2','Xác minh pain · owner · data mapping'],['W3–5','Replay lịch sử, so sánh SOP'],['W6–9','Shadow mode + dữ liệu trễ/sai'],['W10–12','Human-approved pilot / Go-No-Go']];
 pilot.forEach((v,i)=>{let y=2.08+i*.75;box(s,6.90,y,5.70,.60,'EFF5FA');text(s,v[0],7.09,y+.14,1.14,.26,11.5,true,blue);text(s,v[1],8.34,y+.12,4.02,.30,11.5,false,ink);});
 box(s,.70,5.48,11.91,.63,'FFF6ED','E2BD8B');text(s,'STOP CONDITION: data không đủ tin cậy · SOP tốt ngang hoặc hơn · chi phí lớn hơn lợi ích · vi phạm QA/safety.',.9,5.61,11.50,.33,11.8,true,amber);}
// 8 CLOSE
{let s=slide(8);text(s,'KẾT LUẬN: TẠI SAO DENSO NÊN CHỌN THỬ NGHIỆM?',.68,1.44,12,.48,19.0,true,nav);
 note(s,'ĐÃ CHỨNG MINH (TRONG MÔ HÌNH)', '3 kịch bản, 17 test, 24 trường hợp stress, hard constraints, chọn NO_ACTION/VERIFY, có ca thất bại và thử lại được.',.73,2.07,5.76,1.78,green);
 note(s,'CHƯA ĐƯỢC CHỨNG MINH', 'Không có data/SOP của DENSO; chưa có ML causal, ROI, độ chính xác thực địa hay lợi thế hơn hệ thống hiện hữu.',6.78,2.07,5.78,1.78,red);
 box(s,.74,4.17,11.85,1.45,'EAF7F5','A1D4C9');text(s,'PITCH 20 GIÂY',1.01,4.35,3.63,.34,15.2,true,green);
 text(s,'Chúng tôi không thay thế hạ tầng số của DENSO. Chúng tôi đề xuất một lớp kiểm chứng phương án ứng phó: truy từ sự cố tới đơn hàng, kiểm tra ràng buộc, so sánh với SOP và chỉ đề xuất khi dữ liệu đủ tin cậy.',1.01,4.78,11.30,.60,12.1,false,ink,{valign:'top'});
 text(s,'YÊU CẦU PILOT: 1 line · sự cố lịch sử · dữ liệu nối khoá · SOP thực · người phụ trách QA/Production.',.96,5.88,11.58,.28,11.3,true,nav,{align:'center'});}
// 9 OUTRO with verifiable repo
{let s=slide(9);box(s,.57,5.12,9.63,1.43,'0E2C4B','2D7991');text(s,'FACTORYPULSE  |  D3',.85,5.31,7.9,.35,22,true,'FFFFFF');text(s,'Synthetic evidence → Real-data shadow pilot → Go / No-Go',.85,5.77,8.75,.28,12,false,'AAFFE3');s.addImage({path:path.join(R,'assets','github_qr.png'),x:10.51,y:5.10,w:1.57,h:1.57});text(s,'PUBLIC GITHUB',10.47,6.73,1.66,.2,9.5,true,'FFFFFF',{align:'center'});}
p.writeFile({fileName:path.join('/mnt/data','FactoryPulse_D3_2026_BTC_Template_Final.pptx')});
