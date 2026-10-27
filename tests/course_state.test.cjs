const test = require('node:test');
const assert = require('node:assert/strict');
const S = require('../app/web/static/js/course-state.js');
const lesson = {lesson_id:'BK01',revision:'v1',sentences:[1,2,3].map(n=>({sentence_id:`C${n}`,revision:`r${n}`}))};
for (const section of [2,3,4]) test(`section ${section}: review is lossless across reload and lesson browsing`,()=>{
 const state=S.empty();state.lesson_id='BK01';state.section=section;
 const s=S.session(state,lesson,section);s.draft_answer=section===3?'Tôi đang':'我想\n去北京';
 s.completed_answers.C0={correct:true};s.question_index=1;s.sentence_id='C2';
 const original=JSON.stringify(s);S.review(state,s);state.study_id='C3';state.lesson_id='BK02';
 const restored=S.decode(JSON.stringify(state));S.resume(restored);
 assert.equal(restored.lesson_id,'BK01');assert.equal(restored.section,section);
 assert.equal(JSON.stringify(restored.sessions['BK01:'+section]),original);
});
test('repeated review never grades or advances; grading is idempotent',()=>{
 const state=S.empty(),s=S.session(state,lesson,2);s.draft_answer='我想';
 for(let i=0;i<4;i++){S.review(state,s);S.resume(state);}
 assert.equal(s.sentence_id,'C1');assert.deepEqual(s.completed_answers,{});
 S.grade(s,'我想。');S.grade(s,'wrong');assert.equal(Object.keys(s.completed_answers).length,1);
 assert.equal(s.grading_state.correct,true);S.next(s,lesson);assert.equal(s.sentence_id,'C2');
});
test('removed lesson and sentence are explicit recovery, never index substitution',()=>{
 const s=S.create(lesson,2);assert.ok(S.issue(s,null));
 assert.ok(S.issue(s,{...lesson,sentences:lesson.sentences.slice(1)}));
});
test('revision recovery retains draft and unchanged results, archives old grading',()=>{
 const s=S.create(lesson,2);s.draft_answer='我';S.grade(s,'我');
 const changed={...lesson,revision:'v2',sentences:[...lesson.sentences].reverse()};
 assert.ok(S.issue(s,changed));S.reconcile(s,changed,'C1');
 assert.equal(s.draft_answer,'我');assert.equal(s.question_index,2);
 assert.equal(s.grading_state,null);assert.equal(s.archived.length,1);
 assert.equal(s.completed_answers.C1.correct,true);
});
test('edited answer invalidates old result; new target does not inherit draft',()=>{
 const s=S.create(lesson,2);s.draft_answer='draft';S.grade(s,'expected');
 const changed={...lesson,revision:'v2',sentences:lesson.sentences.map(r=>({...r,revision:'changed'}))};
 S.reconcile(s,changed,'C2');assert.equal(s.draft_answer,'');assert.deepEqual(s.completed_answers,{});
 assert.equal(s.archived[0].draft_answer,'draft');
});
test('corrupt state is rejected',()=>assert.throws(()=>S.decode('{"version":99}')));
test('old full-bai draft migrates without loss and review preserves slots',()=>{
 const state=S.empty(),s=S.session(state,lesson,4);s.draft_answer='我想\n北京\n三\n四';
 S.prepareInputs(s,lesson);assert.equal(s.legacy_rewrite_draft,'我想\n北京\n三\n四');
 assert.equal(s.rewrite_drafts.C3,'三\n四');
 S.review(state,s);const restored=S.decode(JSON.stringify(state));S.resume(restored);
 assert.deepEqual(restored.sessions['BK01:4'].rewrite_drafts,s.rewrite_drafts);
});
test('word feedback never changes scores; blank is not an error',()=>{
 assert.equal(S.inputFeedback('','北京'),'');assert.equal(S.inputFeedback('北京','北京'),'correct');
 assert.equal(S.inputFeedback('北经','北京'),'incorrect');
});
