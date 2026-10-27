const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:430,height:932}});
 await page.goto('http://127.0.0.1:8765');await page.locator('[data-mode="course"]').click();
 await page.locator('#courseLesson').selectOption('BK01');await page.locator('[data-section="2"]').click();
 await page.locator('#courseAnswer').fill('我想');await page.locator('#courseReview').click();
 const before=await page.evaluate(()=>JSON.stringify(JSON.parse(localStorage.getItem('chinese-course-v1:user-01')).sessions));
 assert.match(await page.locator('.course-recall').innerText(),/Nghĩa tiếng Việt/);
 assert.match(await page.locator('.course-recall').innerText(),/lữ du/);
 await page.locator('#courseRecallHide').click();assert.equal(await page.locator('#courseStudySource').isVisible(),false);
 await page.locator('#courseRecallAnswer').fill('你');await page.locator('#courseRecallCheck').click();
 assert.match(await page.locator('#courseRecallFeedback').innerText(),/Chưa khớp/);
 const correct='我要去北京旅游， 你觉得\n什么时候去最好';
 await page.locator('#courseRecallAnswer').fill(correct);await page.locator('#courseRecallCheck').click();
 assert.match(await page.locator('#courseRecallFeedback').innerText(),/Đúng rồi/);
 await page.locator('#courseFollowing').click();await page.locator('#courseRecallAnswer').fill('九月');
 await page.locator('#coursePrev').click();assert.equal(await page.locator('#courseRecallAnswer').inputValue(),correct);
 await page.reload();assert.equal(await page.locator('#courseRecallAnswer').inputValue(),correct);
 assert.equal(await page.locator('#courseStudySource').isVisible(),false);
 const after=await page.evaluate(()=>JSON.stringify(JSON.parse(localStorage.getItem('chinese-course-v1:user-01')).sessions));
 assert.equal(after,before);
 for(const width of [320,375,390,430,1280]){
   await page.setViewportSize({width,height:932});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
 }
 await page.setViewportSize({width:430,height:932});await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:'outputs/course-qa/study-recall-430.png',fullPage:true});
 await page.locator('#courseResume').click();assert.equal(await page.locator('#courseAnswer').inputValue(),'我想');
 await browser.close();console.log('PASS study recall: hints, hide, correct/incorrect, drafts per sentence, reload, no impact on practice, responsive');
})().catch(e=>{console.error(e);process.exit(1)});
