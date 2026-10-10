from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math
R=Path(__file__).resolve().parent.parent
asset=R/'assets';asset.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(sz,b=False):return ImageFont.truetype(bold if b else font,sz)
def bg():
 im=Image.new('RGB',(1280,720)); px=im.load()
 for y in range(720):
  for x in range(1280):
   p=x/1280; q=y/720
   px[x,y]=(int(6+18*p),int(21+31*p+9*(1-q)),int(40+35*(1-q)))
 return im
def card(name,title,subtitle,lines,footer):
 im=bg(); d=ImageDraw.Draw(im)
 d.rounded_rectangle([76,65,1204,640],radius=25,outline='#2b737b',width=3,fill='#092638')
 d.text((104,91),'DENSO FACTORY HACKS 2026   /   CHALLENGE D3',font=f(20,True),fill='#73e1c8')
 d.text((104,162),title,font=f(62,True),fill='#eef8ff')
 d.text((106,248),subtitle,font=f(28,True),fill='#51d5bb')
 y=344
 for l in lines:
  d.text((112,y),'• '+l,font=f(23),fill='#d0e5f2');y+=59
 d.text((105,600),footer,font=f(15),fill='#8baabb')
 im.save(asset/name)
card('video_intro.png','FACTORYPULSE','INCIDENT → IMPACT → SAFE DECISION',[
 'D3 / ERP + WMS + MES + QA/TMS',
 'Manual SOP vs integrated information',
 'Synthetic demonstration · Not measured DENSO ROI'],
 'Runnable code and 24 stress cases on public GitHub')
card('video_outro.png','THE VERDICT','EVIDENCE BEFORE PROMISES',[
 '24 stress cases: 5 win · 14 tie · 2 lose · 3 verify',
 '17 automated tests passed in synthetic engine',
 'Pilot needs real SOP timing, data quality and safety approvals'],
 'D3 official 2026 template · Prototype only, no factory validation')
subs=[
(0,11,'Một sự cố máy cắt được nối với ERP, kho, sản xuất và đơn hàng.'),
(11,20.5,'Kịch bản 2: thiếu linh kiện; quyết định phụ thuộc tồn kho và thời gian bổ sung.'),
(20.5,30.5,'Kịch bản 3: QA hold; không thể giải phóng lô hàng trái quy trình.'),
(30.5,41.5,'Đối chứng khó: SOP thủ công nhanh hơn dữ liệu tích hợp. FactoryPulse có thể thua.'),
(41.5,52.5,'Feed đã cũ: VERIFY, không tự đề xuất một hành động rủi ro.'),
(52.5,63,'Tuyến dự phòng không được duyệt hoặc thiếu công suất sẽ bị loại trước khi xếp hạng.'),
(63,71.5,'Nếu không có lợi ích vận hành: hệ thống chọn NO ACTION.'),
(71.5,80.5,'Với dữ liệu đủ mới, cùng một chính sách có thể quyết định sớm hơn.'),
(80.5,89.5,'Thay đổi thời gian tra cứu và feed: hiệu quả có thể đảo chiều.'),
(89.5,98.5,'Kiểm tra QA lần nữa: không bỏ qua cổng phê duyệt.'),
]
def fmt(v):
 h=int(v//3600);m=int(v%3600//60);s=int(v%60);ms=int((v-int(v))*1000)
 return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
text='\n\n'.join(f'{i+1}\n{fmt(a)} --> {fmt(b)}\n{t}' for i,(a,b,t) in enumerate(subs))+'\n'
(asset/'browser_subtitles.srt').write_text(text)
print('video cards and subtitles written')
