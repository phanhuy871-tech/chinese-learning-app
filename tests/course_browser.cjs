/* Run with NODE_PATH pointing at a Playwright installation; server at :8765. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
async function main(){
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:900}});
 const page=await context.newPage(); const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 await page.goto('http://127.0.0.1:8765');
 await page.locator('#courseLesson option').first().waitFor({state:'attached'});
 await page.locator('[data-mode="course"]').click();
 const section=n=>page.locator(`#courseSections [data-section="${n}"]`).click();
 for(const [n,draft] of [[2,'我想'],[3,'Tôi muốn đi'],[4,'我要去北京\n你觉得']]){
   const answer=n===4?'[data-rewrite-id]':'#courseAnswer';
   await section(n); await page.locator(answer).first().fill(draft);
   await page.locator('#courseReview').click();
   await page.locator('#courseFollowing').click();
   await page.locator('#courseLesson').selectOption('BK02');
   await page.reload(); await page.locator('#courseResume').click();
   await page.locator(answer).first().waitFor({state:'visible'});
   assert.equal(await page.locator(answer).first().inputValue(),draft);
   assert.equal(await page.locator('#courseLesson').inputValue(),'BK01');
   await page.locator('#courseReview').click();await page.locator('#courseResume').click();
   assert.equal(await page.locator(answer).first().inputValue(),draft);
 }
 await section(2);await page.locator('#courseCheck').click();
 await page.locator('#courseReview').click();await page.reload();await page.locator('#courseResume').click();
 assert.equal(await page.locator('#courseCheck').count(),0);
 await page.locator('#courseNext').click();await page.locator('#courseAnswer').fill('九月');
 await page.reload();assert.equal(await page.locator('#courseAnswer').inputValue(),'九月');
 assert.match(await page.locator('#courseContent').innerText(),/Đã kiểm tra: 1/);
 // Switching learner isolates sessions and restores the original learner's draft.
 const firstUser=await page.locator('#userSelect').inputValue();
 const otherUser=await page.locator('#userSelect option').nth(1).getAttribute('value');
 await page.locator('#userSelect').selectOption(otherUser);await section(2);
 assert.equal(await page.locator('#courseAnswer').inputValue(),'');
 await page.locator('#courseAnswer').fill('另一个');
 await page.locator('#userSelect').selectOption(firstUser);
 assert.equal(await page.locator('#courseAnswer').inputValue(),'九月');
 // New browser context restores the persisted localStorage snapshot.
 const storage=await context.storageState();
 const reopened=await browser.newContext({storageState:storage});
 const second=await reopened.newPage();await second.goto('http://127.0.0.1:8765');
 await second.locator('#courseAnswer').waitFor({state:'visible'});
 assert.equal(await second.locator('#courseAnswer').inputValue(),'九月');
 await reopened.close();
 // Edited/reordered data must produce explicit recovery, retaining the draft.
 const payload=await (await page.request.get('http://127.0.0.1:8765/api/course/lessons')).json();
 payload.lessons[0].revision='changed';payload.lessons[0].sentences.reverse();
 await page.route('**/api/course/lessons',route=>route.fulfill({json:payload}));
 await page.reload();await page.locator('#courseRecover').waitFor();
 assert.match(await page.locator('#courseContent').innerText(),/cập nhật/);
 await page.locator('#courseRecover').click();assert.equal(await page.locator('#courseAnswer').inputValue(),'九月');
 // Deleted current sentence, then deleted current lesson: safe selection, no crash.
 const currentId='BK01-C02';payload.lessons[0].sentences=payload.lessons[0].sentences.filter(s=>s.sentence_id!==currentId);
 await page.reload();await page.locator('#courseRecover').waitFor();
 assert.match(await page.locator('#courseContent').innerText(),/đã bị xóa/);
 await page.locator('#courseRecover').click();
 payload.lessons=payload.lessons.filter(l=>l.lesson_id!=='BK01');
 await page.reload();await page.locator('#courseContent [role="alert"]').waitFor();
 await page.locator('#courseLesson').selectOption('BK02');
 await page.unroute('**/api/course/lessons');
 fs.mkdirSync('outputs/course-qa',{recursive:true});
 for(const width of [320,375,390,430,1280]){
   await page.setViewportSize({width,height:932});
   await section(2);
   const size=await page.evaluate(()=>({inner:innerWidth,client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
   assert.equal(size.scroll,size.client,JSON.stringify(size));
   await page.evaluate(()=>scrollTo(1000,0));assert.equal(await page.evaluate(()=>scrollX),0);
   await page.screenshot({path:`outputs/course-qa/practice-${width}.png`,fullPage:true});
   await page.locator('#courseReview').click();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
   const illustration=page.locator('#courseContent img').first();
   await illustration.waitFor();
   await page.waitForFunction(()=>document.querySelector('#courseContent img')?.naturalWidth>0);
   await page.locator('#courseWhole').scrollIntoViewIfNeeded();
   assert.equal(await page.locator('#courseResume').evaluate(el=>{
     const r=el.getBoundingClientRect();const target=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
     return target===el||el.contains(target);
   }),true,'Resume button must not be covered by mobile navigation');
   await page.evaluate(()=>scrollTo(0,0));
   await page.screenshot({path:`outputs/course-qa/study-${width}.png`,fullPage:true});
   await page.locator('#courseResume').click();
 }
 assert.deepEqual(errors,[]);
 await browser.close();console.log('PASS browser flows, reload/reopen, revision/deletion recovery, widths 320/375/390/430/1280');
}
main().catch(e=>{console.error(e);process.exit(1)});
