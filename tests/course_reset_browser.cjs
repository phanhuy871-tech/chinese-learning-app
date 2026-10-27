const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:430,height:932}});
 // Never reset a real user's server-side progress during QA.
 let resets=0;
 await page.route('**/api/users/*/progress/reset', async route=>{resets++;await route.fulfill({json:{}});});
 await page.goto('http://127.0.0.1:8765');
 await page.locator('[data-mode="course"]').click();
 await page.locator('[data-section="2"]').click();
 await page.locator('#courseAnswer').fill('我想');
 await page.evaluate(()=>localStorage.setItem('chinese-course-v1:qa-other','preserve'));
 page.once('dialog',d=>d.dismiss());await page.locator('#resetProgress').click();
 assert.equal(await page.locator('#courseAnswer').inputValue(),'我想');assert.equal(resets,0);
 page.once('dialog',d=>d.accept());await page.locator('#resetProgress').click();
 await page.waitForTimeout(150);
 assert.equal(resets,1);
 const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('chinese-course-v1:user-01')));
 assert.deepEqual(state.sessions,{});assert.equal(state.return_target,null);assert.equal(Boolean(state.study_recall && Object.values(state.study_recall).some(r=>r.draft)),false);
 assert.equal(await page.evaluate(()=>localStorage.getItem('chinese-course-v1:qa-other')),'preserve');
 await page.reload();await page.locator('[data-section="2"]').click();
 assert.equal(await page.locator('#courseAnswer').inputValue(),'');
 const data=await (await page.request.get('http://127.0.0.1:8765/api/course/lessons')).json();
 const cat=data.lessons.flatMap(l=>l.sentences).find(s=>s.sentence_id==='BK04-C02');
 assert.equal(cat.hanzi,'那是我的猫，他叫花花');assert.match(cat.pinyin,/māo/);assert.ok(cat.audio_url);
 await browser.close();console.log('PASS reset cancel/confirm, drafts, reload, user isolation, corrected cat and audio');
})().catch(e=>{console.error(e);process.exit(1)});
