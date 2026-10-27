(() => {
  const S = window.CourseState;
  const $ = selector => document.querySelector(selector);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  let lessons = [], state = S.empty(), storageKey = "", storageWarning = "", loadWarning = "";
  function userKey() {return `chinese-course-v1:${selectedUserId}`;}
  function readState() {
    storageKey = userKey(); storageWarning = ""; loadWarning = "";
    try {const raw = localStorage.getItem(storageKey); state = raw ? S.decode(raw) : S.empty();}
    catch {state = S.empty(); loadWarning = "Không đọc được tiến độ đã lưu. Bản lưu cũ chưa bị ghi đè. Chọn phần học để bắt đầu phiên mới.";}
  }
  function save() {
    try {localStorage.setItem(storageKey, JSON.stringify(state)); storageWarning = "";}
    catch {storageWarning = "Trình duyệt không cho lưu tiến độ. Đừng đóng/tải lại trang trước khi sao chép bản nháp.";}
    status();
  }
  function status(message = "") {$("#courseStatus").textContent = [message, loadWarning, storageWarning].filter(Boolean).join(" ");}
  function lessonById(id) {return lessons.find(l => l.lesson_id === id);}
  function currentLesson() {return lessonById(state.lesson_id);}
  function currentSession() {return state.sessions[S.key(state.lesson_id, state.section)];}
  function stopAudio() {if (typeof stopActiveAudio === "function") stopActiveAudio(); else if (activeAudio) activeAudio.pause();}
  function play(row) {
    status(`Đang tải âm thanh · ${row.voice_label}`);
    playAudioSource(row.audio_url || `${appTtsUrl(row.hanzi)}&speaker=${encodeURIComponent(row.speaker)}`)
      .then(()=>status(`Đang phát · ${row.voice_label}`))
      .catch(()=>status("Chưa tải được âm thanh. Kiểm tra mạng/link audio rồi bấm nghe lại."));
  }
  function bindAudio(scope = $("#courseContent")) {
    scope.querySelectorAll("[data-course-audio]").forEach(button => button.onclick = () => {
      const row = currentLesson()?.sentences.find(s => s.sentence_id === button.dataset.courseAudio);
      if (row) play(row);
    });
    scope.querySelectorAll("img").forEach(img => img.onerror = () => {
      const text = document.createElement("p"); text.textContent = "Chưa tải được ảnh minh họa. Kiểm tra tên file/link ảnh."; img.replaceWith(text);
    });
  }
  function card(row) {
    return `<article class="course-card" data-sentence="${esc(row.sentence_id)}">
      <small>${esc(row.speaker)} · ${esc(row.sentence_id)}</small>
      <p class="course-hanzi">${esc(row.hanzi)}</p><p class="pinyin">${esc(row.pinyin)}</p>
      <p>${esc(row.translation_vi)}</p>
      ${row.image_url ? `<img src="${esc(row.image_url)}" alt="Minh họa ${esc(row.sentence_id)}" loading="lazy">` : ""}
      <button type="button" data-course-audio="${esc(row.sentence_id)}">🔊 Nghe câu · ${esc(row.voice_label)}</button>
      ${row.word_glossary?.length ? `<section class="course-glossary"><h4>Từ vựng · Âm Hán Việt · Nghĩa</h4><p>Âm Hán Việt giúp liên hệ từ; khi nói tiếng Trung hãy đọc theo pinyin và audio.</p>${row.word_glossary.map(w=>`<p><strong>${esc(w.hanzi)}</strong> · <b>${esc(w.han_viet)}</b><br>${esc(w.meaning_vi)}</p>`).join("")}</section>` : ""}
      ${row.explanation_vi ? `<p>${esc(row.explanation_vi)}</p>` : ""}
      ${row.vocabulary ? `<p>Từ vựng: ${esc(row.vocabulary)}</p>` : ""}
      ${row.review_queue ? `<details><summary>Ghi chú dữ liệu cần kiểm tra</summary><p class="course-pre">${esc(row.review_queue)}</p></details>` : ""}
    </article>`;
  }
  function renderReturn() {
    const target = state.return_target;
    $("#courseReturn").innerHTML = "";
    if (!target) return;
    const s = state.sessions[S.key(target.lesson_id, target.practice_section)];
    const lesson = lessonById(target.lesson_id);
    const index = lesson?.sentences.findIndex(r => r.sentence_id === s?.sentence_id) ?? -1;
    $("#courseReturn").innerHTML = `<button id="courseResume" type="button">Tiếp tục luyện tập</button>
      <span>Quay lại ${esc(target.lesson_id)} · Phần ${target.practice_section} · ${target.practice_section === 4 ? "Toàn bài" : `Câu ${index + 1}/${lesson?.sentences.length || "?"}`}</span>`;
    $("#courseResume").onclick = () => {stopAudio(); S.resume(state); save(); render();};
  }
  function renderStudy(lesson) {
    const index = Math.max(0, lesson.sentences.findIndex(r => r.sentence_id === state.study_id));
    const row = lesson.sentences[index]; state.study_id = row.sentence_id;
    state.study_recall ||= {};
    const recallKey = `${lesson.lesson_id}:${row.sentence_id}`;
    const recall = state.study_recall[recallKey] ||= {draft: '', hidden: false, feedback: '', revision: row.revision};
    const changed = recall.revision !== row.revision;
    if(changed){recall.feedback='';recall.revision=row.revision;}
    $("#courseContent").innerHTML = `<h3>Phần 1 · Học và hiểu bài khóa</h3>
      <div class="course-toolbar"><button id="coursePrev" ${index === 0 ? "disabled" : ""}>Câu trước</button>
      <label>Câu <select id="courseStudySentence">${lesson.sentences.map((r,i)=>`<option value="${esc(r.sentence_id)}" ${i===index?"selected":""}>${i+1} · ${esc(r.sentence_id)}</option>`).join("")}</select></label>
      <button id="courseFollowing" ${index === lesson.sentences.length-1 ? "disabled" : ""}>Câu sau</button></div>
      <section class="course-recall" aria-label="Viết lại để ghi nhớ">
        <h4>Viết lại để ghi nhớ</h4>
        <p>Luyện ngay tại phần học, không tính điểm và không thay đổi phiên luyện tập đang làm.</p>
        <p><b>Nghĩa tiếng Việt:</b> ${esc(row.translation_vi)}</p>
        <p><b>Âm Hán Việt gợi nhớ:</b> ${esc((row.word_glossary||[]).map(w=>w.han_viet).join(' · ')||'Chưa có dữ liệu.')}</p>
        <details><summary>Nghĩa của các từ gợi nhớ</summary>${(row.word_glossary||[]).map(w=>`<p><b>${esc(w.han_viet)}</b>: ${esc(w.meaning_vi)}</p>`).join('')}<p>Âm Hán Việt không phải cách phát âm Quan thoại; hãy nghe audio để đọc đúng.</p></details>
        <div class="course-toolbar"><button id="courseRecallHide" type="button" aria-pressed="${recall.hidden}">${recall.hidden?'Hiện chữ Hán và pinyin':'Ẩn chữ Hán để tự nhớ'}</button>
        <button type="button" data-course-audio="${esc(row.sentence_id)}">🔊 Nghe · ${esc(row.voice_label)}</button></div>
        ${changed?'<p role="status">Câu nguồn đã cập nhật. Bản nháp được giữ, hãy kiểm tra lại theo nội dung mới.</p>':''}
        <label for="courseRecallAnswer">Tự viết lại chữ Hán của câu này</label>
        <textarea id="courseRecallAnswer" rows="3" autocomplete="off" spellcheck="false" aria-describedby="courseRecallFeedback"></textarea>
        <p id="courseRecallFeedback" role="status" aria-live="polite"></p>
        <div class="course-toolbar"><button id="courseRecallCheck" type="button">Kiểm tra câu vừa viết</button><button id="courseRecallClear" type="button">Xóa bản nháp câu này</button></div>
      </section>
      <div id="courseStudySource" ${recall.hidden?'hidden':''}>${card(row)}<details id="courseWhole"><summary>Xem toàn bộ bài khóa (${lesson.sentences.length} câu)</summary>${lesson.sentences.map(card).join("")}</details></div>`;
    const go = id => {stopAudio(); state.study_id=id; save(); render();};
    $("#coursePrev").onclick = () => go(lesson.sentences[index-1].sentence_id);
    $("#courseFollowing").onclick = () => go(lesson.sentences[index+1].sentence_id);
    $("#courseStudySentence").onchange = e => go(e.target.value);
    const recallInput=$('#courseRecallAnswer');recallInput.value=recall.draft;
    let composing=false;
    const feedback=()=>{
      recallInput.dataset.feedback=recall.feedback;
      recallInput.setAttribute('aria-invalid',String(recall.feedback==='incorrect'));
      $('#courseRecallFeedback').textContent=recall.feedback==='correct'?'✓ Đúng rồi! Bạn đã viết lại đúng câu.':recall.feedback==='incorrect'?'Chưa khớp câu mẫu. Thử sửa lại hoặc bấm Hiện chữ Hán để đối chiếu.':'';
    };
    recallInput.oncompositionstart=()=>{composing=true;recall.feedback='';feedback();};
    recallInput.oncompositionend=()=>{composing=false;recall.draft=recallInput.value;save();};
    recallInput.oninput=()=>{recall.draft=recallInput.value;recall.feedback='';feedback();save();};
    $('#courseRecallCheck').onclick=()=>{
      if(composing)return status('Hãy chọn xong chữ Hán trước khi kiểm tra.');
      if(!recall.draft.trim())return status('Nhập câu bạn nhớ trước khi kiểm tra.');
      recall.feedback=S.inputFeedback(recall.draft,row.hanzi);feedback();save();
    };
    $('#courseRecallHide').onclick=()=>{
      recall.hidden=!recall.hidden;$('#courseStudySource').hidden=recall.hidden;
      $('#courseRecallHide').textContent=recall.hidden?'Hiện chữ Hán và pinyin':'Ẩn chữ Hán để tự nhớ';
      $('#courseRecallHide').setAttribute('aria-pressed',String(recall.hidden));save();
    };
    $('#courseRecallClear').onclick=()=>{recall.draft='';recall.feedback='';recallInput.value='';feedback();save();recallInput.focus();};
    feedback();
    bindAudio();
  }
  function recovery(s, lesson, problem) {
    $("#courseContent").innerHTML = `<p role="alert">${esc(problem)}</p>
      <label>Bản nháp đã lưu<textarea readonly>${esc(s?.draft_answer || "")}</textarea></label>
      ${lesson ? `<label>Tiếp tục tại câu<select id="courseRecoverySentence">${lesson.sentences.map(r=>`<option value="${esc(r.sentence_id)}" ${r.sentence_id===s.sentence_id?"selected":""}>${esc(r.sentence_id)} · ${esc(r.hanzi)}</option>`).join("")}</select></label><button id="courseRecover">Xác nhận vị trí tiếp tục</button>` : "<p>Chọn bài khác ở danh sách phía trên. Phiên cũ không bị xóa.</p>"}`;
    if (lesson) $("#courseRecover").onclick = () => {S.reconcile(s, lesson, $("#courseRecoverySentence").value); save(); render();};
  }
  function answerInputs(s, lesson, row) {
    const locked=s.grading_state?'readonly':'';
    if(state.section===4) return `<p>Mỗi ô viết một câu theo nghĩa bên dưới. Âm Hán Việt là gợi nhớ theo từ, không phải bản dịch cả câu.</p>
      ${s.legacy_rewrite_draft?`<details><summary>Bản nháp toàn bài trước khi chia ô</summary><p class="course-pre">${esc(s.legacy_rewrite_draft)}</p></details>`:''}
      <div class="course-rewrite">${lesson.sentences.map((r,i)=>`<section class="course-rewrite-row">
        <label for="rewrite-${i}"><b>Câu ${i+1} · ${esc(r.speaker)}</b></label>
        <p><b>Nghĩa tiếng Việt:</b> ${esc(r.translation_vi||'Chưa có bản dịch.')}</p>
        <p><b>Âm Hán Việt (từ gợi nhớ):</b> ${esc((r.word_glossary||[]).map(w=>w.han_viet).join(' · ')||'Chưa có dữ liệu.')}</p>
        <textarea id="rewrite-${i}" data-rewrite-id="${esc(r.sentence_id)}" rows="2" aria-label="Viết lại câu ${i+1}" aria-describedby="rewrite-feedback-${i}" autocomplete="off" spellcheck="false" ${locked}></textarea>
        <span id="rewrite-feedback-${i}" class="course-input-feedback" aria-live="polite"></span>
      </section>`).join('')}</div>`;
    const tokens=row.listening_tokens||[];
    const toggle=state.section===2?`<label class="course-assist-toggle"><input type="checkbox" id="courseAssist" ${s.assisted?'checked':''} ${!tokens.length||s.grading_state?'disabled':''}> Hỗ trợ từng từ/cụm</label>
      <small>${tokens.length?'Hai chế độ giữ bản nháp riêng. Kiểm tra khi chọn xong chữ Hán hoặc rời ô; chưa hiện đáp án.':'Câu này chưa có cách tách từ đã duyệt; hãy nhập cả câu.'}</small>`:'';
    if(state.section===2&&s.assisted&&tokens.length) return `${toggle}<div class="course-token-grid">${tokens.map((t,i)=>`<label class="course-token-cell">Từ/cụm ${i+1}
      <input data-token-index="${i}" aria-label="Từ hoặc cụm ${i+1}" aria-describedby="token-feedback-${i}" autocomplete="off" spellcheck="false" ${locked}>
      <span id="token-feedback-${i}" class="course-input-feedback" aria-live="polite"></span></label>`).join('')}</div>`;
    return `${toggle}<label for="courseAnswer">${state.section===3?'Bản dịch tiếng Việt':'Nội dung chữ Hán'}</label>
      <textarea id="courseAnswer" rows="3" autocomplete="off" spellcheck="false" ${locked}></textarea>`;
  }
  function bindAnswerInputs(s, lesson, row) {
    const show=(input,expected,key,check)=>{
      if(check)s.input_checks[key]=S.inputFeedback(input.value,expected);
      const result=s.input_checks[key]||'';
      input.dataset.feedback=result;
      input.setAttribute('aria-invalid',String(result==='incorrect'));
      const message=document.getElementById(input.getAttribute('aria-describedby'));
      if(message)message.textContent=result==='correct'?'✓ Đúng':result==='incorrect'?'Chưa đúng, hãy thử sửa lại.':'';
    };
    const wire=(input,expected,key,onEdit)=>{
      let composing=false;
      input.addEventListener('compositionstart',()=>{composing=true;input.dataset.composing='true';delete s.input_checks[key];show(input,expected,key,false);});
      input.addEventListener('input',e=>{onEdit();delete s.input_checks[key];show(input,expected,key,false);save();});
      input.addEventListener('compositionend',()=>{composing=false;input.dataset.composing='false';onEdit();show(input,expected,key,true);save();});
      input.addEventListener('blur',()=>{if(!composing){onEdit();show(input,expected,key,true);save();}});
      show(input,expected,key,false);
    };
    if($('#courseAssist'))$('#courseAssist').onchange=e=>{
      if(e.target.checked){s.free_draft=s.draft_answer;s.assisted=true;s.draft_answer=(s.token_drafts[row.sentence_id]||[]).join('');}
      else{s.assisted=false;s.draft_answer=s.free_draft||'';}
      save();render();
    };
    document.querySelectorAll('[data-token-index]').forEach(input=>{
      const i=Number(input.dataset.tokenIndex),tokens=row.listening_tokens;
      const drafts=s.token_drafts[row.sentence_id] ||= tokens.map(()=> '');
      input.value=drafts[i]||'';
      wire(input,tokens[i],`${row.sentence_id}:word:${i}`,()=>{drafts[i]=input.value;s.draft_answer=drafts.join('');});
    });
    document.querySelectorAll('[data-rewrite-id]').forEach(input=>{
      const id=input.dataset.rewriteId,r=lesson.sentences.find(r=>r.sentence_id===id);
      input.value=s.rewrite_drafts[id]||'';
      input.addEventListener('focus',()=>{s.sentence_id=id;s.question_index=lesson.sentences.indexOf(r);save();});
      wire(input,r.hanzi,`${id}:rewrite`,()=>{s.rewrite_drafts[id]=input.value;s.draft_answer=lesson.sentences.map(r=>s.rewrite_drafts[r.sentence_id]||'').join('\n');});
    });
  }
  function renderPractice(lesson) {
    const s = S.session(state, lesson, state.section);
    const problem = S.issue(s, lesson);
    if (problem) return recovery(s, lesson, problem);
    S.prepareInputs(s,lesson);
    const index = lesson.sentences.findIndex(r => r.sentence_id === s.sentence_id);
    s.question_index = index;
    const row = lesson.sentences[index];
    const expected = state.section === 4 ? lesson.sentences.map(r=>r.hanzi).join("\n") : state.section === 3 ? row.translation_vi : row.hanzi;
    const done = Object.values(s.completed_answers);
    const heading = state.section===2 ? "Phần 2 · Nghe và nhập lại chữ Hán" : state.section===3 ? "Phần 3 · Đọc chữ Hán và dịch tiếng Việt" : "Phần 4 · Viết lại nội dung bài khóa";
    $("#courseContent").innerHTML = `<div class="course-practice-head"><h3>${heading}</h3><button id="courseReview">📖 Xem lại bài học</button></div>
      <p>${state.section===4?"Viết toàn bộ bài theo thứ tự câu (không cần ghi A/B).":`Câu ${index+1}/${lesson.sentences.length} · ${esc(row.sentence_id)}`}</p>
      <p>Đã kiểm tra: ${done.length} · Khớp mẫu / tự xác nhận: ${done.filter(r=>r.correct).length}</p>
      ${s.finished ? `<h3>Đã hoàn thành lượt luyện</h3><button id="courseRestart">Luyện lại phần này</button>` : `
      ${state.section===2 ? `<button data-course-audio="${esc(row.sentence_id)}">🔊 Nghe câu · ${esc(row.voice_label)}</button>` : state.section===3 ? `<p class="course-hanzi">${esc(row.hanzi)}</p>` : ""}
      <details><summary>Gợi ý</summary><p class="course-pre">${esc(state.section===4?lesson.sentences.map(r=>r.hint_pinyin).join("\n"):state.section===3?row.hint_vi:row.hint_pinyin)}</p></details>
      ${answerInputs(s,lesson,row)}
      ${s.grading_state ? `<div role="status"><p>${s.grading_state.correct?"✓ Khớp mẫu / đã tự xác nhận":"Chưa khớp đáp án mẫu — không đồng nghĩa bản dịch khác là sai."}</p><p class="course-pre">Đáp án mẫu: ${esc(s.grading_state.expected)}</p></div>
      ${state.section===3&&!s.grading_state.correct?'<button id="courseAccept">Bản dịch của tôi tương đương (tự đánh giá)</button>':""}
      <button id="courseNext">${state.section===4||index===lesson.sentences.length-1?"Hoàn thành lượt":"Câu tiếp theo"}</button>` : '<button id="courseCheck">Kiểm tra đáp án</button>'}`}
      ${done.length?`<details><summary>Kết quả đã lưu</summary>${Object.entries(s.completed_answers).map(([id,r])=>`<p>${esc(id)}: ${esc(r.draft)} — ${r.correct?"✓":"Chưa khớp mẫu"}</p>`).join("")}</details>`:""}
      ${s.archived.length?`<details><summary>Bản nháp trước khi cập nhật/luyện lại</summary>${s.archived.map(a=>`<p class="course-pre">${esc(a.sentence_id)}: ${esc(a.draft_answer)}</p>`).join("")}</details>`:""}`;
    $("#courseReview").onclick = () => {stopAudio(); S.review(state,s); save(); render();};
    const input = $("#courseAnswer");
    if(input) {input.value=s.draft_answer; input.oninput=()=>{s.draft_answer=input.value; save();};}
    bindAnswerInputs(s,lesson,row);
    if($("#courseCheck")) $("#courseCheck").onclick = () => {
      if(document.querySelector('#courseContent [data-composing="true"]'))return status('Hãy chọn xong chữ Hán trước khi kiểm tra.');
      if(!expected.trim())return status("Câu này chưa có đáp án mẫu trong dữ liệu; chưa thể kiểm tra.");
      if(!s.draft_answer.trim())return status("Nhập câu trả lời trước khi kiểm tra.");
      const result=S.grade(s,expected);
      if(state.section===4)result.correct=lesson.sentences.every(r=>S.normalize(s.rewrite_drafts[r.sentence_id]||'')===S.normalize(r.hanzi));
      if(state.section===2&&s.assisted)result.correct=row.listening_tokens.every((t,i)=>S.normalize(s.token_drafts[row.sentence_id]?.[i]||'')===S.normalize(t));
      s.completed_answers[state.section===4?s.segment_id:s.sentence_id]={...result};save();render();
    };
    if($("#courseNext")) $("#courseNext").onclick = () => {S.next(s,lesson); save(); render();};
    if($("#courseAccept")) $("#courseAccept").onclick = () => {s.grading_state.correct=true;s.grading_state.self_assessed=true;s.completed_answers[s.sentence_id]={...s.grading_state};save();render();};
    if($("#courseRestart")) $("#courseRestart").onclick = () => {
      const fresh=S.create(lesson,state.section);fresh.archived=[...s.archived,JSON.parse(JSON.stringify({...s,archived:[]}))].slice(-10);
      state.sessions[S.key(lesson.lesson_id,state.section)]=fresh;save();render();
    };
    bindAudio();
  }
  function render() {
    const picker=$("#courseLesson");
    picker.innerHTML = lessons.map(l=>`<option value="${esc(l.lesson_id)}">${esc(l.lesson_id)} · ${esc(l.sentences[0].hanzi.slice(0,22))} (${l.sentences.length} câu)</option>`).join("");
    picker.value=state.lesson_id || "";
    $("#courseSections").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed",String(Number(b.dataset.section)===state.section)));
    renderReturn();
    const lesson=currentLesson();
    if(!lesson) {recovery(currentSession(),null,"Bài đã lưu không còn trong dữ liệu. Chọn bài khóa để tiếp tục.");return;}
    if(state.section===1)renderStudy(lesson);else renderPractice(lesson);
  }
  async function load(refresh=false) {
    try {
      const response=await fetch(`/api/course/${refresh?"refresh":"lessons"}`,{method:refresh?"POST":"GET"});
      if(!response.ok)throw new Error("Không tải được bài khóa. Dữ liệu/tiến độ cũ vẫn được giữ.");
      lessons=(await response.json()).lessons;
      if(!state.lesson_id&&lessons.length)state.lesson_id=lessons[0].lesson_id;
      status(refresh?"Đã cập nhật dữ liệu bài khóa.":""); render();
      if(!refresh) {try {if(localStorage.getItem("chinese-course-active")==="true") switchMode("course");} catch { /* optional UI preference */ }}
    }catch(error){status(error.message);}
  }
  readState(); load();
  document.querySelectorAll(".mode").forEach(button=>button.addEventListener("click",()=>{
    try {localStorage.setItem("chinese-course-active",String(button.dataset.mode==="course"));} catch { /* draft saving reports errors separately */ }
  }));
  $("#courseLesson").onchange=e=>{stopAudio();state.lesson_id=e.target.value;state.study_id=null;save();render();};
  $("#courseSections").onclick=e=>{const b=e.target.closest("[data-section]");if(!b)return;stopAudio();state.section=Number(b.dataset.section);if(state.section!==1)state.return_target=null;loadWarning="";save();render();};
  $("#courseRefresh").onclick=()=>load(true);
  window.addEventListener("learning-progress-reset",()=>{
    stopAudio();state=S.empty();state.lesson_id=lessons[0]?.lesson_id || null;
    loadWarning="";save();render();
  });
  window.addEventListener("learning-user-changed",()=>{stopAudio();readState();if(!state.lesson_id)state.lesson_id=lessons[0]?.lesson_id;render();});
  // Input events persist synchronously, including drafts before review or navigation.
})();
