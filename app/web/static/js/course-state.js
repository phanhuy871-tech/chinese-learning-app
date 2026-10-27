/* Pure, versioned state transitions: rendering never submits an answer. */
(function (root) {
  const clone = value => JSON.parse(JSON.stringify(value));
  const key = (lesson, section) => `${lesson}:${section}`;
  const empty = () => ({version: 1, sessions: {}, lesson_id: null, section: 1, study_id: null, return_target: null});
  function create(lesson, section) {
    return {lesson_id: lesson.lesson_id, practice_section: section, segment_id: lesson.lesson_id,
      sentence_id: lesson.sentences[0].sentence_id, question_index: 0, draft_answer: "",
      completed_answers: {}, grading_state: null, revision: lesson.revision,
      sentence_revisions: Object.fromEntries(lesson.sentences.map(s => [s.sentence_id, s.revision])),
      finished: false, archived: []};
  }
  function session(state, lesson, section) {
    const k = key(lesson.lesson_id, section);
    return state.sessions[k] ||= create(lesson, section);
  }
  function issue(s, lesson) {
    if (!lesson) return "Bài khóa đã bị xóa hoặc đổi mã. Phiên cũ vẫn được lưu; hãy chọn một bài hợp lệ.";
    if (!lesson.sentences.some(row => row.sentence_id === s.sentence_id))
      return "Câu đang làm đã bị xóa hoặc đổi mã. Chọn câu hợp lệ để tiếp tục; bản nháp cũ được giữ trong bản lưu.";
    if (s.revision !== lesson.revision)
      return "Nội dung hoặc thứ tự bài đã cập nhật. Xác nhận vị trí tiếp tục trước khi luyện; bản nháp cũ được giữ lại.";
    return "";
  }
  function reconcile(s, lesson, sentenceId) {
    s.archived.push(clone({...s, archived: []}));
    s.archived = s.archived.slice(-10);
    const same = sentenceId === s.sentence_id;
    const updated = lesson.sentences.find(r => r.sentence_id === sentenceId);
    if (!updated) throw new Error("Unknown sentence ID");
    const keep = {};
    for (const row of lesson.sentences) {
      if (s.sentence_revisions[row.sentence_id] === row.revision && s.completed_answers[row.sentence_id])
        keep[row.sentence_id] = s.completed_answers[row.sentence_id];
    }
    if (s.practice_section === 4) s.completed_answers = {};
    else s.completed_answers = keep;
    s.draft_answer = same || s.practice_section === 4 ? s.draft_answer : "";
    s.grading_state = null;
    s.finished = false;
    s.input_checks = {};
    s.token_drafts = {};
    s.assisted = false;
    s.sentence_id = sentenceId;
    s.question_index = lesson.sentences.findIndex(r => r.sentence_id === sentenceId);
    s.revision = lesson.revision;
    s.sentence_revisions = Object.fromEntries(lesson.sentences.map(r => [r.sentence_id, r.revision]));
  }
  function review(state, s) {
    state.return_target = {lesson_id: s.lesson_id, practice_section: s.practice_section};
    state.lesson_id = s.lesson_id;
    state.study_id = s.sentence_id;
    state.section = 1;
  }
  function resume(state) {
    const t = state.return_target;
    if (!t) return;
    state.lesson_id = t.lesson_id;
    state.section = t.practice_section;
    state.return_target = null;
  }
  const normalize = text => text.normalize("NFC").toLocaleLowerCase("vi").replace(/[\p{P}\p{Z}\s]/gu, "");
  function prepareInputs(s, lesson) {
    s.token_drafts ||= {};
    s.input_checks ||= {};
    if (s.practice_section === 4 && !s.rewrite_drafts) {
      s.rewrite_drafts = {};
      // Keep the original whole-bài draft intact while mapping its existing lines.
      s.legacy_rewrite_draft = s.draft_answer;
      const lines = s.draft_answer.split('\n');
      lesson.sentences.forEach((r,i)=>{s.rewrite_drafts[r.sentence_id]=i===lesson.sentences.length-1?lines.slice(i).join('\n'):(lines[i]||'');});
    }
  }
  function inputFeedback(value, expected) {
    return !normalize(value) ? '' : normalize(value) === normalize(expected) ? 'correct' : 'incorrect';
  }
  function grade(s, expected) {
    if (s.grading_state) return s.grading_state;
    const result = {draft: s.draft_answer, expected, correct: normalize(s.draft_answer) === normalize(expected), self_assessed: false};
    s.grading_state = result;
    s.completed_answers[s.practice_section === 4 ? s.segment_id : s.sentence_id] = clone(result);
    return result;
  }
  function next(s, lesson) {
    if (!s.grading_state) return;
    const index = lesson.sentences.findIndex(r => r.sentence_id === s.sentence_id);
    if (s.practice_section === 4 || index === lesson.sentences.length - 1) {s.finished = true; return;}
    s.question_index = index + 1;
    s.sentence_id = lesson.sentences[index + 1].sentence_id;
    s.draft_answer = "";
    s.free_draft = "";
    s.grading_state = null;
  }
  function decode(raw) {
    const s = JSON.parse(raw);
    if (!s || s.version !== 1 || typeof s.sessions !== "object" || !s.sessions || ![1,2,3,4].includes(s.section)) throw new Error("Invalid saved state");
    for (const p of Object.values(s.sessions)) {
      if (!p || typeof p.lesson_id !== "string" || ![2,3,4].includes(p.practice_section) ||
          typeof p.draft_answer !== "string" || typeof p.completed_answers !== "object" || !p.completed_answers ||
          !p.sentence_revisions || !Array.isArray(p.archived)) throw new Error("Invalid practice session");
    }
    return s;
  }
  const api = {empty, key, create, session, issue, reconcile, review, resume, grade, next, decode, normalize, prepareInputs, inputFeedback};
  if (typeof module !== "undefined") module.exports = api;
  else root.CourseState = api;
})(typeof window === "undefined" ? globalThis : window);
