let monoSession = null;

function monoMeaning(card) {
  return (card.meaning_vi || "").trim();
}

// Preserve ü and explicit tones. Untoned input remains a spelling exercise.
function monoPinyin(value) {
  const raw = value.toLowerCase().trim().replace(/u:/g, "ü").replace(/v/g, "ü").normalize("NFD");
  const tones = {"\u0304": "1", "\u0301": "2", "\u030c": "3", "\u0300": "4"};
  const marks = [...raw].filter(c => tones[c]).map(c => tones[c]);
  const digits = raw.match(/[0-5]/g) || [];
  const base = raw.replace(/u\u0308/g, "v").replace(/[\u0300-\u036f0-5\s'’]/g, "");
  return {base, tone: (digits[0] === "0" ? "5" : digits[0]) || marks[0] || "5", explicit: Boolean(digits.length || marks.length), valid: /^[a-zv]+$/.test(base) && digits.length <= 1 && marks.length <= 1 && !(digits.length && marks.length)};
}

function monoPinyinMatches(answer, expected) {
  const a = monoPinyin(answer), b = monoPinyin(expected);
  return a.valid && b.valid && a.base === b.base && (!a.explicit || a.tone === b.tone);
}

function monoReadings(card) {
  return [...new Set([card.pinyin, ...(card.readings || []).map(r => r.pinyin)].filter(Boolean))];
}

function monoHanziMatches(answer, question) {
  return (question.accepted || [question.card.simplified, question.card.traditional]).includes(answer.trim().normalize("NFC"));
}

function monoGameQuestions(cards) {
  const kinds = ["meaning", "pinyin", "character"];
  return shuffleItems(cards).slice(0, 10).map((card, index) => {
    const kind = kinds[index % kinds.length];
    const answerFor = item => kind === "meaning" ? monoMeaning(item) : kind === "pinyin" ? item.pinyin.trim().toLowerCase() : item.simplified;
    const correct = answerFor(card);
    const seen = new Set([correct]);
    const alternatives = [];
    for (const item of shuffleItems(cards)) {
      const answer = answerFor(item);
      // Same-meaning characters cannot be used as distractors for a meaning prompt.
      if (!answer || seen.has(answer) || (kind === "character" && monoMeaning(item) === monoMeaning(card)) || (kind === "pinyin" && monoReadings(card).includes(answer))) continue;
      alternatives.push(answer);
      seen.add(answer);
      if (alternatives.length === 3) break;
    }
    return {card, kind, correct, options: shuffleItems([correct, ...alternatives])};
  }).filter(question => question.options.length >= 2);
}

function monoTypingQuestions(cards) {
  return shuffleItems(cards).slice(0, 10).map(card => ({ card, kind: "hanziInput", correct: card.simplified,
    accepted: cards.filter(c => monoMeaning(c) === monoMeaning(card)).flatMap(c => [c.simplified, c.traditional]).filter(Boolean) }));
}

function startMonoGame(review = null, mode = "choice") {
  monoFlash = null;
  const cards = filteredMonolithic().filter(card => card.simplified && card.pinyin && monoMeaning(card));
  const questions = review || (mode === "typing" ? monoTypingQuestions(cards) : monoGameQuestions(cards));
  if (!questions.length) {
    document.querySelector("#monolithicDetail").textContent = "Cần ít nhất hai chữ khác nhau để chơi. Hãy chọn thêm tuần hoặc bỏ lọc cốt lõi.";
    return;
  }
  monoSession = {questions, index: 0, correct: 0, wrong: [], locked: false, review: Boolean(review), mode};
  document.body.classList.add("mono-playing");
  renderMonoQuestion();
  scrollMonolithicIntoView();
}

function leaveMonoGame() {
  monoSession = null;
  monoFlash = null;
  document.body.classList.remove("mono-playing");
  renderMonolithicList();
}

function renderMonoQuestion() {
  const session = monoSession;
  const question = session.questions[session.index];
  const box = document.querySelector("#monolithicDetail");
  if (!question) {
    box.innerHTML = `<div class="mono-game"><h3>${session.review ? "Đã ôn xong!" : "Hoàn thành lượt chơi!"}</h3>
      <p class="mono-score">${session.correct}/${session.questions.length} câu đúng</p>
      <p>${session.wrong.length ? "Ôn lại các câu sai để nhớ lâu hơn nhé." : "Tốt lắm! Thử lượt mới để học thêm chữ nhé."}</p>
      <div class="mono-game-actions">${session.wrong.length ? '<button id="monoReview" type="button">Ôn câu sai</button>' : ""}<button id="monoAgain" type="button">Chơi lượt mới</button><button id="monoExit" class="secondary-button" type="button">Về bài học</button></div></div>`;
    document.querySelector("#monoReview")?.addEventListener("click", () => startMonoGame(shuffleItems(session.wrong), session.mode));
    document.querySelector("#monoAgain").onclick = () => startMonoGame(null, session.mode);
    document.querySelector("#monoExit").onclick = leaveMonoGame;
    return;
  }
  session.locked = false;
  const prompt = question.kind === "character" ? monoMeaning(question.card) : question.card.simplified;
  if (session.mode === "typing") {
    box.innerHTML = `<div class="mono-game"><div class="mono-game-actions"><span>Câu ${session.index + 1}/${session.questions.length} · Đúng ${session.correct}</span><button id="monoExit" class="secondary-button" type="button">Về bài học</button></div><progress aria-label="Tiến độ lượt chơi" value="${session.index}" max="${session.questions.length}"></progress><h3>Nhập chữ Hán ứng với nghĩa này</h3><div class="mono-game-prompt is-meaning">${escapeHtml(monoMeaning(question.card))}</div><input id="monoHanziInput" class="mono-hanzi-input" inputmode="text" autocomplete="off" placeholder="Nhập chữ Hán…" aria-label="Chữ Hán trả lời"><button id="monoCheckHanzi" type="button">Kiểm tra</button><div id="monoFeedback" role="status" aria-live="polite"></div><div class="mono-game-actions"><button id="monoNext" type="button" hidden>Câu tiếp theo →</button></div></div>`;
    document.querySelector("#monoExit").onclick = leaveMonoGame;
    document.querySelector("#monoCheckHanzi").onclick = () => {
      if (session.locked) return;
      const answer = document.querySelector("#monoHanziInput").value.trim();
      if (!answer) return;
      session.locked = true;
      const correct = monoHanziMatches(answer, question);
      document.querySelector("#monoHanziInput").disabled = true;
      document.querySelector("#monoCheckHanzi").disabled = true;
      if (correct) session.correct += 1; else session.wrong.push(question);
      document.querySelector(".mono-game-actions > span").textContent = `Câu ${session.index + 1}/${session.questions.length} · Đúng ${session.correct}`;
      document.querySelector("#monoFeedback").innerHTML = `<p><strong>${correct ? "Đúng rồi!" : "Chưa đúng — đáp án là:"}</strong></p><p class="mono-answer-reveal">${escapeHtml(question.card.simplified)} · ${escapeHtml(question.card.pinyin)}</p><p>${escapeHtml(monoMeaning(question.card))}</p>`;
      document.querySelector("#monoNext").hidden = false;
      document.querySelector("#monoNext").focus({preventScroll:true});
    };
    document.querySelector("#monoHanziInput").addEventListener("keydown", event => {
      if (event.key === "Enter" && !event.isComposing && event.keyCode !== 229) { event.preventDefault(); document.querySelector("#monoCheckHanzi").click(); }
    });
    document.querySelector("#monoNext").onclick = () => { if (!session.locked) return; session.index += 1; renderMonoQuestion(); };
    return;
  }
  const instruction = {meaning: "Chữ này có nghĩa là gì?", pinyin: "Chọn pinyin đúng", character: "Nghĩa này ứng với chữ nào?"}[question.kind];
  box.innerHTML = `<div class="mono-game"><div class="mono-game-actions"><span>Câu ${session.index + 1}/${session.questions.length} · Đúng ${session.correct}</span><button id="monoExit" class="secondary-button" type="button">Về bài học</button></div>
    <progress aria-label="Tiến độ lượt chơi" value="${session.index}" max="${session.questions.length}"></progress>
    <h3>${instruction}</h3><div class="mono-game-prompt ${question.kind === "character" ? "is-meaning" : ""}">${escapeHtml(prompt)}</div>
    <div class="mono-game-options">${question.options.map((option, index) => `<button class="mono-answer" data-choice="${index}" type="button">${escapeHtml(option)}</button>`).join("")}</div>
    <div id="monoFeedback" role="status" aria-live="polite"></div>
    <div class="mono-game-actions"><button id="monoListen" class="secondary-button" type="button" hidden>Nghe phát âm</button><button id="monoNext" type="button" hidden>Câu tiếp theo →</button></div></div>`;
  document.querySelector("#monoExit").onclick = leaveMonoGame;
  document.querySelectorAll(".mono-answer").forEach(button => button.onclick = () => {
    if (session.locked) return;
    session.locked = true;
    const chosen = question.options[Number(button.dataset.choice)];
    const correct = chosen === question.correct;
    if (correct) session.correct += 1;
    else session.wrong.push(question);
    document.querySelector(".mono-game-actions > span").textContent = `Câu ${session.index + 1}/${session.questions.length} · Đúng ${session.correct}`;
    document.querySelectorAll(".mono-answer").forEach(answer => {
      answer.disabled = true;
      if (question.options[Number(answer.dataset.choice)] === question.correct) answer.classList.add("is-correct");
    });
    if (!correct) button.classList.add("is-wrong");
    const card = question.card;
    document.querySelector("#monoFeedback").innerHTML = `<p><strong>${correct ? "Đúng rồi!" : "Chưa đúng — cùng ghi nhớ nhé:"}</strong></p><p>${escapeHtml(card.simplified)} · ${escapeHtml(card.pinyin)} · ${escapeHtml(card.han_viet)}</p><p>${escapeHtml(monoMeaning(card))}</p>`;
    document.querySelector("#monoListen").hidden = false;
    document.querySelector("#monoNext").hidden = false;
    document.querySelector("#monoNext").focus({preventScroll: true});
  });
  document.querySelector("#monoListen").onclick = () => speakWord(question.card.readings?.[0]?.audio_text || question.card.simplified, "");
  document.querySelector("#monoNext").onclick = () => {
    if (!session.locked) return;
    session.index += 1;
    renderMonoQuestion();
  };
}

document.querySelector("#startMonoGame").onclick = () => startMonoGame();
document.querySelector("#startMonoTypingGame").onclick = () => startMonoGame(null, "typing");

let monoFlash = null;
function flashMemoryKey() { return `mono-flash-v1:${selectedUserId}`; }
function readFlashMemory() {
  try { const value = JSON.parse(localStorage.getItem(flashMemoryKey()) || "{}"); return value && typeof value === "object" && !Array.isArray(value) ? value : {}; }
  catch { return {}; }
}

function startMonoFlash(cards = null) {
  monoSession = null;
  const memory = readFlashMemory();
  const pool = cards || shuffleItems(filteredMonolithic()).sort((a, b) => (memory[a.id]?.due || 0) - (memory[b.id]?.due || 0)).slice(0, 10);
  if (!pool.length) return;
  monoFlash = {queue: [...pool], total: pool.length, remembered: 0, attempts: {}, difficult: [], flipped: false, memory, key: flashMemoryKey()};
  document.body.classList.add("mono-playing");
  renderMonoFlash();
  scrollMonolithicIntoView();
}

function renderMonoFlash() {
  const state = monoFlash;
  const card = state.queue[0];
  const box = document.querySelector("#monolithicDetail");
  if (!card) {
    box.innerHTML = `<div class="mono-game"><h3>Đã học xong ${state.total} thẻ!</h3><p>Đã nhớ: ${state.remembered} · Cần ôn thêm: ${state.difficult.length}</p><p>Thẻ khó sẽ được ưu tiên ở lượt sau. Tiến độ lưu theo người học trên thiết bị này.</p><div class="mono-game-actions"><button id="flashMore">Học 10 thẻ tiếp</button>${state.difficult.length ? '<button id="flashReview">Ôn thẻ khó</button>' : ''}<button id="flashExit" class="secondary-button">Về bài học</button></div></div>`;
    document.querySelector("#flashMore").onclick = () => startMonoFlash();
    document.querySelector("#flashReview")?.addEventListener("click", () => startMonoFlash(state.difficult));
    document.querySelector("#flashExit").onclick = leaveMonoGame;
    return;
  }
  state.flipped = false;
  state.pinyinChecked = false;
  box.innerHTML = `<div class="mono-game"><div class="mono-game-actions"><strong>Flashcard · Còn ${state.queue.length} lượt</strong><button id="flashExit" class="secondary-button">Về bài học</button></div>
    <p>Nhập pinyin có dấu hoặc số thanh (rén / ren2). Không dấu chỉ kiểm tra âm; ü có thể gõ v hoặc u:. Chấp nhận các cách đọc đã ghi trong bài.</p>
    <div id="flashCard" class="mono-flash-card" aria-label="Mặt trước flashcard"><span class="flash-hanzi">${escapeHtml(card.simplified)}</span><span id="flashBack" hidden><strong>${escapeHtml(card.pinyin)}</strong><span>Hán Việt: ${escapeHtml(card.han_viet)}</span><span>${escapeHtml(card.meaning_vi)}</span>${card.examples?.[0] ? `<small>${escapeHtml(card.examples[0].hanzi)}<br>${escapeHtml(card.examples[0].pinyin)}<br>${escapeHtml(card.examples[0].meaning_vi)}</small>` : ""}<small>Dạng thành phần: ${escapeHtml(card.radical_form || card.simplified)}</small></span><small id="flipHint">Chưa mở đáp án</small></div>
    <div class="flash-pinyin-check"><label for="flashPinyin">Pinyin bạn nhớ</label><div><input id="flashPinyin" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Ví dụ: ni hao" /><button id="flashCheckPinyin" type="button">Kiểm tra</button></div><p id="flashPinyinStatus" role="status"></p></div>
    <div class="mono-game-actions"><button id="flashSound" class="secondary-button">Nghe tiếng phổ thông</button><button id="flashReveal" class="secondary-button">Chưa nhớ · Xem đáp án</button></div>
    <div id="flashRatings" class="mono-game-actions" hidden><button id="flashAgain" class="flash-again">Chưa nhớ · Ôn lại</button><button id="flashKnown">Đã nhớ ✓</button></div><p id="flashSaveStatus" role="status"></p></div>`;
  document.querySelector("#flashExit").onclick = leaveMonoGame;
  document.querySelector("#flashSound").onclick = () => speakWord(card.readings?.[0]?.audio_text || card.simplified, "");
  const reveal = (checked, message) => {
    state.pinyinChecked = checked;
    state.flipped = true;
    document.querySelector("#flashBack").hidden = false;
    document.querySelector("#flashCard").setAttribute("aria-label", "Đáp án flashcard");
    document.querySelector("#flipHint").textContent = checked ? "Đã kiểm tra cách đọc" : "Đáp án để ôn lại";
    document.querySelector("#flashPinyinStatus").textContent = message;
    document.querySelector("#flashRatings").hidden = false;
    document.querySelector("#flashKnown").disabled = !checked;
  };
  document.querySelector("#flashReveal").onclick = () => reveal(false, "Cùng đọc và ghi nhớ. Chọn Ôn lại để gặp lại thẻ này, hoặc nhập đúng pinyin để tiếp tục.");
  document.querySelector("#flashCheckPinyin").onclick = () => {
    const answer = document.querySelector("#flashPinyin").value.trim();
    if (!answer) { document.querySelector("#flashPinyinStatus").textContent = "Hãy nhập pinyin hoặc chọn Xem đáp án."; return; }
    const matched = monoReadings(card).find(expected => monoPinyinMatches(answer, expected));
    if (!matched) {
      state.pinyinChecked = false;
      document.querySelector("#flashKnown").disabled = true;
      document.querySelector("#flashPinyinStatus").textContent = "Chưa đúng, thử lại nhé. Nghe mẫu nếu cần.";
      document.querySelector("#flashPinyin").select();
      return;
    }
    const note = matched !== card.pinyin ? ` Bạn nhập cách đọc ${matched}; mặt sau hiển thị cách đọc chính ${card.pinyin}. Xem phần Phân biệt cách đọc trong bài học.` : "";
    reveal(true, (monoPinyin(answer).explicit ? "Đúng cách đọc và thanh điệu! Xem nghĩa rồi tự đánh giá." : "Đúng phần âm. Bạn chưa nhập thanh điệu; xem dấu thanh trong đáp án nhé.") + note);
  };
  document.querySelector("#flashPinyin").addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.isComposing && event.keyCode !== 229) { event.preventDefault(); document.querySelector("#flashCheckPinyin").click(); }
  });
  const rate = known => {
    if (!state.flipped || (known && !state.pinyinChecked) || state.queue[0] !== card) return;
    state.queue.shift();
    const previous = state.memory[card.id] || {};
    const days = known ? Math.min(30, previous.days ? previous.days * 2 : 1) : 0;
    state.memory[card.id] = {days, due: Date.now() + days * 86400000};
    try { localStorage.setItem(state.key, JSON.stringify(state.memory)); } catch { /* Current session still works when storage is unavailable. */ }
    if (known) state.remembered += 1;
    else {
      state.attempts[card.id] = (state.attempts[card.id] || 0) + 1;
      if (state.attempts[card.id] === 1) state.queue.splice(Math.min(3, state.queue.length), 0, card);
      else state.difficult.push(card);
    }
    renderMonoFlash();
  };
  document.querySelector("#flashAgain").onclick = () => rate(false);
  document.querySelector("#flashKnown").onclick = () => rate(true);
}
document.querySelector("#startMonoFlash").onclick = () => startMonoFlash();
