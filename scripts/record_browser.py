import asyncio,os
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parent.parent
async def main():
 out=R/'assets'/'recorded';out.mkdir(parents=True,exist_ok=True)
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=await browser.new_context(viewport={'width':1680,'height':1000},device_scale_factor=1,record_video_dir=str(out),record_video_size={'width':1280,'height':720})
  page=await context.new_page();page_errors=[];page.on('pageerror',lambda e:page_errors.append(str(e)))
  await page.set_content((R/'standalone.html').read_text(),wait_until='load');await page.wait_for_function('window.FactoryPulse!==undefined')
  async def wait(message,ms):print(message,flush=True);await page.wait_for_timeout(ms)
  await wait('01 Normal machine impact + comparison',11000)
  await page.evaluate("window.FactoryPulse.setIncident('material')");await wait('02 Component shortage',9500)
  await page.evaluate("window.FactoryPulse.setIncident('quality')");await wait('03 QA hold + approved alternative',10000)
  await page.evaluate("window.FactoryPulse.setIncident('machine');window.FactoryPulse.setFixture('fastManual')");await wait('04 Manual SOP is faster',11000)
  await page.evaluate("window.FactoryPulse.setFixture('stale')");await wait('05 Stale feed requires verification',11000)
  await page.evaluate("window.FactoryPulse.setFixture('noApproval')");await wait('06 Forbidden backup',10500)
  await page.evaluate("window.FactoryPulse.setFixture('neutral')");await wait('07 No need to intervene',8500)
  await page.evaluate("window.FactoryPulse.setFixture('normal')");await wait('08 Same policy fresh feed',9000)
  await page.locator('#manual').fill('0');await page.locator('#feed').fill('35');await wait('09 Sensitivity manual beats integration',9000)
  await page.evaluate("window.FactoryPulse.setIncident('quality')");await wait('10 QA release constrained',9000)
  vid=page.video
  await context.close()
  origin=await vid.path()
  (R/'assets'/'video_path.txt').write_text(origin)
  print('VIDEO_PATH '+origin,flush=True)
  print('ERRORS',page_errors,flush=True)
  await browser.close()
if __name__=='__main__':asyncio.run(main())
