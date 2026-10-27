const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:430,height:932}});
 await page.goto('http://127.0.0.1:8765');
 await page.locator('[data-mode="course"]').click();
 await page.locator('#courseLesson').selectOption('BK01');
 await page.locator('#courseSections [data-section="1"]').click();
 await page.locator('.course-glossary').first().waitFor();
 assert.match(await page.locator('.course-glossary').first().innerText(),/lữ du/);
 const data=await (await page.request.get('http://127.0.0.1:8765/api/course/lessons')).json();
 const urls=data.lessons.flatMap(l=>l.sentences.map(s=>s.audio_url));
 const durations=await page.evaluate(async urls=>{
   const context=new AudioContext();const result=[];
   for(const url of urls){const r=await fetch(url);if(!r.ok)throw Error('missing audio '+url);
     const b=await context.decodeAudioData(await r.arrayBuffer());result.push(b.duration);}
   await context.close();return result;
 },urls);
 assert.equal(durations.length,20);assert.ok(durations.every(d=>d>0.5));
 for(const [speaker,sex] of [['A','nữ'],['B','nam']]){
   if(speaker==='B')await page.locator('#courseFollowing').click();
   const button=page.locator('#courseContent [data-course-audio]').first();
   assert.match(await button.innerText(),new RegExp(`giọng ${sex}`));await button.click();
   await page.waitForFunction(()=>activeAudio && !activeAudio.paused && activeAudio.currentTime>0.2);
   assert.equal(await page.evaluate(()=>activeAudio.error),null);
 }
 await page.screenshot({path:'outputs/course-qa/audio-hanviet-430.png',fullPage:true});
 console.log(JSON.stringify({decoded:durations.length,minDuration:Math.min(...durations),maxDuration:Math.max(...durations),playback:'A and B passed'}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
