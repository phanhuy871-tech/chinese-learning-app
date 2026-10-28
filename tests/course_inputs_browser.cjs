const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:430,height:932}});
 await page.goto('http://127.0.0.1:8765');await page.locator('[data-mode="course"]').click();
 await page.locator('#courseLesson').selectOption('BK01');
 await page.locator('[data-section="2"]').click();await page.locator('#courseAnswer').fill('我想');
 await page.locator('#courseAssist').check();
 assert.equal(await page.locator('#token-hint-3').innerText(),'2 chữ Hán · Đầu pinyin: B J');
 assert.equal(await page.locator('#token-hint-7').innerText(),'4 chữ Hán · Đầu pinyin: S M S H');
 const first=page.locator('[data-token-index="0"]');
 await first.fill('你');await first.blur();assert.equal(await first.getAttribute('aria-invalid'),'true');
 assert.match(await page.locator('#token-feedback-0').innerText(),/Chưa đúng/);
 await first.dispatchEvent('compositionstart');await first.fill('wo');
 assert.equal(await page.locator('#token-feedback-0').innerText(),'');
 await first.fill('我');await first.dispatchEvent('compositionend');
 assert.equal(await page.locator('#token-feedback-0').innerText(),'✓ Đúng');
 await page.locator('[data-token-index="1"]').fill('要');
 await page.locator('#courseReview').click();await page.reload();await page.locator('#courseResume').click();
 assert.equal(await first.inputValue(),'我');assert.equal(await page.locator('[data-token-index="1"]').inputValue(),'要');
 assert.equal(await page.locator('#token-feedback-0').innerText(),'✓ Đúng');
 assert.match(await page.locator('#courseContent').innerText(),/Đã kiểm tra: 0/);
 await page.locator('#courseAssist').uncheck();assert.equal(await page.locator('#courseAnswer').inputValue(),'我想');
 await page.locator('#courseAssist').check();assert.equal(await first.inputValue(),'我');
 for(const width of [320,375,390,430,1280]){
   await page.setViewportSize({width,height:932});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
 }
 await page.setViewportSize({width:430,height:932});
 await page.screenshot({path:'outputs/course-qa/token-inputs-430.png',fullPage:true});
 await page.locator('[data-section="3"]').click();assert.equal(await page.locator('#courseAssist').count(),0);
 assert.equal(await page.locator('#courseAnswer').count(),1);
 await page.locator('[data-section="4"]').click();
 assert.equal(await page.locator('[data-rewrite-id]').count(),4);
 assert.match(await page.locator('.course-rewrite-row').first().innerText(),/Nghĩa tiếng Việt/);
 assert.match(await page.locator('.course-rewrite-row').first().innerText(),/lữ du/);
 const r1=page.locator('[data-rewrite-id="BK01-C01"]'),r2=page.locator('[data-rewrite-id="BK01-C02"]');
 await r1.fill('我要去');await r2.fill('九月');
 await page.locator('#courseReview').click();
 assert.equal(await page.locator('#courseStudySentence').inputValue(),'BK01-C02');
 await page.reload();await page.locator('#courseResume').click();
 assert.equal(await r1.inputValue(),'我要去');assert.equal(await r2.inputValue(),'九月');
 for(const width of [320,375,390,430,1280]){
   await page.setViewportSize({width,height:932});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);
 }
 await page.setViewportSize({width:430,height:932});
 await page.screenshot({path:'outputs/course-qa/rewrite-inputs-430.png',fullPage:true});
 await browser.close();console.log('PASS IME feedback, separate drafts, slots restore, translation free input, rewrite hints, five viewport sizes');
})().catch(e=>{console.error(e);process.exit(1)});
