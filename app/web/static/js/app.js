let selectedLesson = 1;
let selectedGame = "hanzi_to_pinyin";
let vocabularyCards = [];
let radicalCards = [];
let grammarCards = [];
let users = [];
let selectedUserId = localStorage.getItem("selectedUserId") || "user-01";
let currentProgress = emptyProgress();
let selectedWordId = "";

let currentQuestion = null;
let currentQuestionIndex = 0;
let score = 0;
let answered = false;
let orderingSelection = [];
let visibleExampleCount = 3;

const progressStorageKey = "chineseLearningProgressV1";
const audioLikeGames = new Set(["audio_to_hanzi", "audio_to_pinyin", "audio_to_meaning"]);
const mobileMedia = window.matchMedia("(max-width: 820px)");
const gameLabels = {
  audio_to_hanzi: "Nghe âm thanh, chọn chữ Hán",
  audio_to_pinyin: "Nghe âm thanh, chọn pinyin",
  audio_to_meaning: "Nghe âm thanh, chọn nghĩa",
  hanzi_to_audio: "Nhìn chữ Hán, chọn âm thanh",
  hanzi_to_pinyin: "Nhìn chữ Hán, chọn pinyin",
  hanzi_to_meaning: "Nhìn chữ Hán, chọn nghĩa",
  pinyin_to_hanzi: "Nhìn pinyin, chọn chữ Hán",
  pinyin_to_meaning: "Nhìn pinyin, chọn nghĩa",
  sentence_ordering: "Sắp xếp câu",
  sentence_blank: "Điền từ vào câu",
};

function emptyProgress() {
  // Cấu trúc dữ liệu tiến độ lưu cho từng người học.
  return {
    studiedWords: {},
    answered: 0,
    correct: 0,
    wrong: 0,
  };
}

function readProgress() {
  // Đọc tiến độ đang giữ trong bộ nhớ frontend.
  return { ...emptyProgress(), ...currentProgress };
}

async function saveProgressToServer(progress) {
  // Lưu tiến độ vào SQLite backend theo người học đang chọn.
  const response = await fetch(`/api/users/${selectedUserId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(progress),
  });
  return response.json();
}

function saveProgress(progress) {
  // Lưu vào bộ nhớ frontend trước để giao diện phản hồi ngay, sau đó đồng bộ backend.
  currentProgress = { ...emptyProgress(), ...progress };
  localStorage.setItem(progressStorageKey, JSON.stringify(progress));
  saveProgressToServer(currentProgress).catch(() => {
    // Nếu server tạm lỗi, tiến độ vẫn còn trong localStorage để không mất thao tác học.
  });
}

function progressAccuracy(progress) {
  // Tính tỉ lệ đúng, tránh chia cho 0 khi chưa làm câu nào.
  if (!progress.answered) {
    return "0%";
  }
  return `${Math.round((progress.correct / progress.answered) * 100)}%`;
}

function renderProgress() {
  // Cập nhật các ô thống kê tiến độ trên giao diện.
  const progress = readProgress();
  document.querySelector("#progressWords").textContent = Object.keys(progress.studiedWords || {}).length;
  document.querySelector("#progressAnswered").textContent = progress.answered;
  document.querySelector("#progressCorrect").textContent = progress.correct;
  document.querySelector("#progressAccuracy").textContent = progressAccuracy(progress);
}

async function loadProgressForUser(userId) {
  // Tải tiến độ của người học từ backend SQLite.
  selectedUserId = userId;
  localStorage.setItem("selectedUserId", selectedUserId);
  try {
    const response = await fetch(`/api/users/${selectedUserId}/progress`);
    currentProgress = { ...emptyProgress(), ...(await response.json()) };
  } catch {
    try {
      currentProgress = { ...emptyProgress(), ...JSON.parse(localStorage.getItem(progressStorageKey) || "{}") };
    } catch {
      currentProgress = emptyProgress();
    }
  }
  renderProgress();
}

function renderUsers() {
  // Hiện danh sách người học trong dropdown.
  const select = document.querySelector("#userSelect");
  select.innerHTML = users
    .map((user) => `<option value="${escapeHtml(user.id)}">${escapeHtml(user.name)}</option>`)
    .join("");
  select.value = selectedUserId;
}

async function loadUsers() {
  // Lấy 10 người học mặc định từ backend, rồi tải tiến độ của người đang chọn.
  const response = await fetch("/api/users");
  users = await response.json();
  if (!users.some((user) => user.id === selectedUserId)) {
    selectedUserId = users[0]?.id || "user-01";
  }
  renderUsers();
  await loadProgressForUser(selectedUserId);
}

function recordStudiedWord(word) {
  // Mỗi từ đã mở trong phần chi tiết sẽ được tính là đã xem.
  const progress = readProgress();
  progress.studiedWords = progress.studiedWords || {};
  progress.studiedWords[word.id] = true;
  saveProgress(progress);
  renderProgress();
}

function recordGameAnswer(isCorrect) {
  // Mỗi lần trả lời game sẽ tăng tổng câu, đúng hoặc sai.
  const progress = readProgress();
  progress.answered += 1;
  if (isCorrect) {
    progress.correct += 1;
  } else {
    progress.wrong += 1;
  }
  saveProgress(progress);
  renderProgress();
}

function questionSpeechText(question) {
  // Tìm nội dung tiếng Trung nên đọc cho câu hỏi hiện tại.
  return question.explanation?.hanzi || question.explanation?.sentence_hanzi || question.hanzi || question.question_text || "";
}

function escapeHtml(value) {
  // Bảo vệ giao diện: nếu dữ liệu Sheet có ký tự HTML, không cho nó chèn code vào trang.
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function showAudioStatus(message, isError = false) {
  // Hiển thị phản hồi ngắn để người học biết nút nghe đã nhận thao tác.
  let status = document.querySelector("#audioStatus");
  if (!status) {
    status = document.createElement("div");
    status.id = "audioStatus";
    status.className = "audio-status";
    document.body.appendChild(status);
  }
  status.textContent = message;
  status.classList.toggle("is-error", isError);
  status.classList.add("is-visible");
  window.clearTimeout(showAudioStatus.timer);
  showAudioStatus.timer = window.setTimeout(() => status.classList.remove("is-visible"), 2600);
}

function googleTtsUrl(text) {
  // Fallback cuối cùng nếu backend TTS chưa sẵn sàng.
  const query = encodeURIComponent(String(text || "").slice(0, 180));
  return `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-CN&q=${query}`;
}

function appTtsUrl(text) {
  // Endpoint Python tạo MP3 bằng giọng neural tiếng Trung, ổn định hơn giọng của iPhone/browser.
  return `/api/tts?text=${encodeURIComponent(String(text || "").slice(0, 180))}`;
}

function playAudioSource(source) {
  // Tạo audio mới cho mỗi lần bấm để mobile coi đây là thao tác phát do người dùng khởi tạo.
  const audio = new Audio(source);
  audio.preload = "auto";
  return audio.play();
}

function speakWithBrowserVoice(text) {
  // Dùng Web Speech API nếu trình duyệt có sẵn giọng đọc tiếng Trung.
  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
    return false;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  const voices = window.speechSynthesis.getVoices();
  const chineseVoice = voices.find((voice) => voice.lang.toLowerCase().startsWith("zh"));
  if (chineseVoice) {
    utterance.voice = chineseVoice;
  }
  utterance.lang = "zh-CN";
  utterance.rate = 0.88;
  utterance.volume = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
  return true;
}

function speakWord(text, audioUrl) {
  // Ưu tiên nguồn audio chuẩn: file riêng trong Sheet, rồi tới backend TTS tiếng Trung của app.
  // Giọng trình duyệt chỉ là fallback cuối cùng vì iPhone có thể chọn nhầm giọng và đọc sai âm Hán.
  const speakText = String(text || "").trim();
  const source = audioUrl || (speakText ? appTtsUrl(speakText) : "");
  if (source) {
    playAudioSource(source)
      .then(() => showAudioStatus("Đang phát âm thanh"))
      .catch(() => {
        playAudioSource(googleTtsUrl(speakText))
          .then(() => showAudioStatus("Đang phát âm thanh dự phòng"))
          .catch(() => {
            if (speakWithBrowserVoice(speakText)) {
              showAudioStatus("Đang phát bằng giọng của trình duyệt");
              return;
            }
            showAudioStatus("Máy này chưa phát được âm thanh. Hãy thử bật âm lượng và tắt chế độ im lặng.", true);
          });
      });
    return;
  }

  showAudioStatus("Chưa có dữ liệu âm thanh cho mục này.", true);
}

function explainQuestion(question) {
  const explanation = question.explanation || {};
  return [
    explanation.hanzi || explanation.sentence_hanzi || "",
    explanation.pinyin || explanation.sentence_pinyin || "",
    explanation.meaning_vi || explanation.sentence_vi || "",
  ]
    .filter(Boolean)
    .join(" · ");
}

function completedBlankSentence(question) {
  // Dùng cho game điền từ: hiện câu hoàn chỉnh sau khi người học trả lời.
  if (question.game_type !== "sentence_blank") {
    return "";
  }
  const answerOption = question.options?.find((option) => option.id === question.answer_id);
  const answer = answerOption?.value || answerOption?.text || question.explanation?.blank_hanzi || "";
  const blank = question.question_text || "";
  if (!answer || !blank) {
    return "";
  }
  return blank.replace("___", answer);
}

function explanationParts(question) {
  // Chuẩn hóa giải thích sau khi trả lời thành 3 dòng: Hán tự, pinyin, nghĩa.
  const explanation = question.explanation || {};
  const completed = completedBlankSentence(question);
  const hanzi = completed || explanation.hanzi || explanation.sentence_hanzi || "";
  const pinyin = explanation.pinyin || explanation.sentence_pinyin || "";
  const meaning = explanation.meaning_vi || explanation.sentence_vi || "";
  return { hanzi, pinyin, meaning };
}

function renderFeedbackContent(title, question) {
  // Dùng HTML có escape để kết quả game câu dễ đọc hơn trên điện thoại.
  const parts = explanationParts(question);
  const rows = [
    ["Hán tự", parts.hanzi],
    ["Pinyin", parts.pinyin],
    ["Nghĩa", parts.meaning],
  ]
    .filter(([, value]) => value)
    .map(
      ([label, value]) => `
        <div class="feedback-row">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `,
    )
    .join("");

  return `
    <div class="feedback-title">${escapeHtml(title)}</div>
    <div class="feedback-details">${rows}</div>
  `;
}

async function switchMode(mode) {
  // Đổi module đang xem: study, radicals, grammar, hoặc game.
  document.querySelectorAll(".mode").forEach((item) => {
    item.classList.toggle("is-active", item.dataset.mode === mode);
  });
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.classList.toggle("hidden", panel.dataset.panel !== mode);
  });
  if (mode === "radicals" && !radicalCards.length) {
    await loadRadicals();
  }
  if (mode === "grammar") {
    await loadGrammar();
  }
  if (mode === "game") {
    await loadQuestion();
  }
}

async function loadQuestion() {
  // Gọi backend để tạo 1 câu hỏi game theo loại game và bài đang chọn.
  const box = document.querySelector("#questionBox");
  box.innerHTML = '<div class="empty-state">Đang tạo câu hỏi...</div>';
  const response = await fetch(
    `/api/games/${selectedGame}/question?lesson_order=${selectedLesson}&item_index=${currentQuestionIndex}`,
  );
  const data = await response.json();
  if (!response.ok) {
    box.innerHTML = `<div class="game-feedback is-wrong">${escapeHtml(data.detail || "Không tạo được câu hỏi.")}</div>`;
    return;
  }
  currentQuestion = data;
  answered = false;
  orderingSelection = [];
  renderGameQuestion(data);
}

function renderGamePrompt(question) {
  if (audioLikeGames.has(question.game_type)) {
    return `
      <div class="game-prompt">
        <button class="play-question sound-button" type="button">Nghe câu hỏi</button>
        <p>${escapeHtml(question.prompt)}</p>
      </div>
    `;
  }

  if (question.game_type === "sentence_blank") {
    const highlightedBlank = escapeHtml(question.question_text || "").replaceAll("___", '<span class="blank-slot">___</span>');
    return `
      <div class="game-prompt">
        <div class="prompt-head">
          <div class="prompt-text">${highlightedBlank}</div>
          <button class="play-question sound-button" type="button">Phát âm</button>
        </div>
        <p>Chọn từ phù hợp để điền vào chỗ trống.</p>
      </div>
    `;
  }

  if (question.game_type === "sentence_ordering") {
    return `
      <div class="game-prompt">
        <div class="prompt-head">
          <div class="prompt-text">${escapeHtml(question.question_text || question.prompt)}</div>
          <button class="play-question sound-button" type="button">Phát âm</button>
        </div>
        <p>Sắp xếp các mảnh từ thành câu đúng.</p>
      </div>
    `;
  }

  return `
    <div class="game-prompt">
      <div class="prompt-head">
        <div class="prompt-text">${escapeHtml(question.hanzi || question.pinyin || question.meaning_vi || question.question_text)}</div>
        <button class="play-question sound-button" type="button">Phát âm</button>
      </div>
      <p>${escapeHtml(question.prompt)}</p>
    </div>
  `;
}

function renderOption(option, question) {
  const optionIndex = question.options.findIndex((item) => item.id === option.id) + 1;
  if (question.game_type === "hanzi_to_audio") {
    return `
      <div class="audio-choice">
        <button
          class="play-option"
          data-audio-url="${escapeHtml(option.audio_url)}"
          data-speak-value="${escapeHtml(option.value)}"
          type="button"
        >
          Nghe ${optionIndex}
        </button>
        <button class="answer-option" data-option-id="${escapeHtml(option.id)}" type="button">
          Chọn ${optionIndex}
        </button>
      </div>
    `;
  }

  const label = option.text || option.value || "Nghe";
  return `
    <button
      class="answer-option"
      data-option-id="${escapeHtml(option.id)}"
      data-audio-url="${escapeHtml(option.audio_url)}"
      data-speak-value="${escapeHtml(option.value)}"
      type="button"
    >
      ${escapeHtml(label)}
    </button>
  `;
}

function renderGameQuestion(question) {
  const box = document.querySelector("#questionBox");
  const options = question.options.map((option) => renderOption(option, question)).join("");
  const orderingArea = question.game_type === "sentence_ordering" ? '<div id="orderingAnswer" class="ordering-answer"></div>' : "";

  box.innerHTML = `
    <div class="game-card">
      <div class="game-meta">
        <span>${escapeHtml(gameLabels[question.game_type] || question.game_type)}</span>
        <span>Điểm: <strong id="scoreText">${score}</strong></span>
        <span>Câu: <strong>${currentQuestionIndex + 1}</strong></span>
      </div>
      ${renderGamePrompt(question)}
      ${orderingArea}
      <div class="answer-grid">${options}</div>
      ${
        question.game_type === "sentence_ordering"
          ? `
            <div class="ordering-tools">
              <button id="undoOrdering" class="tool-button" type="button">Hoàn tác</button>
              <button id="resetOrdering" class="tool-button" type="button">Làm lại</button>
            </div>
          `
          : ""
      }
      <div id="gameFeedback" class="game-feedback"></div>
      <div class="game-actions">
        <button id="nextQuestion" class="next-button" type="button" disabled>Câu tiếp theo</button>
      </div>
    </div>
  `;

  const playQuestion = box.querySelector(".play-question");
  if (playQuestion) {
    playQuestion.addEventListener("click", () => speakWord(questionSpeechText(question), question.audio_url));
  }

  box.querySelectorAll(".answer-option").forEach((button) => {
    button.addEventListener("click", () => handleAnswer(button.dataset.optionId));
  });

  box.querySelectorAll(".play-option").forEach((button) => {
    button.addEventListener("click", () => speakWord(button.dataset.speakValue, button.dataset.audioUrl));
  });

  box.querySelector("#nextQuestion").addEventListener("click", async () => {
    currentQuestionIndex += 1;
    await loadQuestion();
  });

  const undoOrdering = box.querySelector("#undoOrdering");
  if (undoOrdering) {
    undoOrdering.addEventListener("click", undoOrderingStep);
  }

  const resetOrdering = box.querySelector("#resetOrdering");
  if (resetOrdering) {
    resetOrdering.addEventListener("click", resetOrderingAnswer);
  }

  if (audioLikeGames.has(question.game_type)) {
    speakWord(questionSpeechText(question), question.audio_url);
  }
}

function handleAnswer(optionId) {
  if (!currentQuestion || answered) {
    return;
  }

  if (currentQuestion.game_type === "sentence_ordering") {
    handleOrderingAnswer(optionId);
    return;
  }

  answered = true;
  const isCorrect = optionId === currentQuestion.answer_id;
  showResult(isCorrect, optionId);
}

function handleOrderingAnswer(optionId) {
  const option = currentQuestion.options.find((item) => item.id === optionId);
  if (!option) {
    return;
  }

  orderingSelection.push({
    optionId,
    text: option.value || option.text,
  });
  const answerBox = document.querySelector("#orderingAnswer");
  answerBox.textContent = orderingSelection.map((item) => item.text).join(" ");
  const clickedButton = document.querySelector(`[data-option-id="${CSS.escape(optionId)}"]`);
  if (clickedButton) {
    clickedButton.disabled = true;
  }

  const expectedParts = currentQuestion.answer_id.split("|");
  if (orderingSelection.length < expectedParts.length) {
    return;
  }

  answered = true;
  const isCorrect = orderingSelection.map((item) => item.text).join("|") === currentQuestion.answer_id;
  showResult(isCorrect, optionId);
}

function undoOrderingStep() {
  if (answered || currentQuestion?.game_type !== "sentence_ordering" || !orderingSelection.length) {
    return;
  }
  const last = orderingSelection.pop();
  const button = document.querySelector(`[data-option-id="${CSS.escape(last.optionId)}"]`);
  if (button) {
    button.disabled = false;
  }
  document.querySelector("#orderingAnswer").textContent = orderingSelection.map((item) => item.text).join(" ");
}

function resetOrderingAnswer() {
  if (answered || currentQuestion?.game_type !== "sentence_ordering") {
    return;
  }
  orderingSelection = [];
  document.querySelector("#orderingAnswer").textContent = "";
  document.querySelectorAll(".answer-option").forEach((button) => {
    button.disabled = false;
  });
}

function markOptions(selectedOptionId) {
  // Sau khi trả lời, khóa các đáp án và tô màu đúng/sai.
  document.querySelectorAll(".answer-option").forEach((button) => {
    button.disabled = true;
    if (button.dataset.optionId === currentQuestion.answer_id) {
      button.classList.add("is-answer");
    }
    if (selectedOptionId && button.dataset.optionId === selectedOptionId && selectedOptionId !== currentQuestion.answer_id) {
      button.classList.add("is-selected-wrong");
    }
  });
}

function showResult(isCorrect, selectedOptionId) {
  const feedback = document.querySelector("#gameFeedback");
  const nextButton = document.querySelector("#nextQuestion");
  markOptions(selectedOptionId);
  recordGameAnswer(isCorrect);

  if (isCorrect) {
    score += 1;
    feedback.className = "game-feedback is-correct";
    feedback.innerHTML = renderFeedbackContent("Đúng", currentQuestion);
  } else {
    feedback.className = "game-feedback is-wrong";
    feedback.innerHTML = renderFeedbackContent("Chưa đúng. Đáp án đúng", currentQuestion);
  }

  document.querySelector("#scoreText").textContent = score;
  nextButton.disabled = false;
}

function renderWordList(cards) {
  // Hiện danh sách từ vựng của bài đang chọn ở cột giữa.
  const list = document.querySelector("#wordList");
  if (!cards.length) {
    list.innerHTML = '<div class="empty-state">Chưa có từ vựng cho bài này.</div>';
    return;
  }
  list.innerHTML = cards
    .map((card, index) => {
      const word = card.word;
      const isActive = word.id === selectedWordId ? " is-active" : "";
      return `
        <button class="word-item${isActive}" data-word-index="${index}" type="button">
          <span class="hanzi">${escapeHtml(word.hanzi)}</span>
          <span>${escapeHtml(word.pinyin)} · ${escapeHtml(word.meaning_vi)}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".word-item").forEach((button) => {
    // Khi bấm vào 1 từ, cập nhật cột "Chi tiết" bên phải.
    button.addEventListener("click", () => {
      renderWordDetail(cards[Number(button.dataset.wordIndex)]);
      if (mobileMedia.matches) {
        document.querySelector("#wordDetail").scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

function renderWordDetail(card, showAll = false) {
  // Hiện chi tiết 1 từ: chữ Hán, pinyin, nghĩa, chiết tự, ví dụ, bộ thủ liên quan.
  const detail = document.querySelector("#wordDetail");
  const word = card.word;
  selectedWordId = word.id;
  visibleExampleCount = showAll ? card.sentences.length : mobileMedia.matches ? 3 : 5;
  document.querySelectorAll(".word-item").forEach((button) => {
    const item = vocabularyCards[Number(button.dataset.wordIndex)]?.word;
    button.classList.toggle("is-active", item?.id === selectedWordId);
  });
  recordStudiedWord(word);
  const visibleSentences = card.sentences.slice(0, visibleExampleCount);
  const examples = visibleSentences.length
    ? visibleSentences
        .map(
          (sentence) => `
            <li>
              <div class="example-head">
                <strong>${escapeHtml(sentence.sentence_hanzi)}</strong>
                <button
                  class="sentence-sound"
                  data-speak-value="${escapeHtml(sentence.sentence_hanzi)}"
                  data-audio-url="${escapeHtml(sentence.audio_url || "")}"
                  type="button"
                >
                  Nghe câu
                </button>
              </div>
              <span>${escapeHtml(sentence.sentence_pinyin)}</span>
              <em>${escapeHtml(sentence.sentence_vi)}</em>
            </li>
          `,
        )
        .join("")
    : `<li><em>Chưa có câu ví dụ sẵn sàng cho từ này.</em></li>`;
  const moreExamples =
    card.sentences.length > visibleExampleCount
      ? `<button class="show-more-examples" type="button">Xem thêm ${card.sentences.length - visibleExampleCount} câu</button>`
      : "";

  const radicals = card.radicals.length
    ? card.radicals
        .map(
          (radical) => `
            <details class="radical">
              <summary>
                <strong>${escapeHtml(radical.radical)}</strong>
                <span>${escapeHtml(radical.han_viet)} · ${escapeHtml(radical.pinyin)} · ${escapeHtml(radical.meaning_vi)}</span>
              </summary>
              <p>${escapeHtml(radical.memory_tip)}</p>
              <p>${escapeHtml(radical.semantic_note)}</p>
            </details>
            <button class="radical-link" data-radical-id="${escapeHtml(radical.id)}" type="button">Học bộ này</button>
          `,
        )
        .join("")
    : `<p class="muted">Chưa tìm thấy bộ thủ liên quan trong tab bộ thủ.</p>`;

  detail.innerHTML = `
    <div class="word-detail-head">
      <div>
        <div class="big-hanzi">${escapeHtml(word.hanzi)}</div>
        <p>${escapeHtml(word.pinyin)} · ${escapeHtml(word.meaning_vi)}</p>
      </div>
      <button class="sound-button" type="button">Nghe</button>
    </div>
    <section>
      <h3>Chiết từ</h3>
      <p>${escapeHtml(word.decomposition || "Chưa có dữ liệu chiết từ.")}</p>
    </section>
    <section>
      <h3>Ví dụ</h3>
      <ul class="examples">${examples}</ul>
      ${moreExamples}
    </section>
    <section>
      <h3>Bộ thủ liên quan</h3>
      ${radicals}
    </section>
  `;

  detail.querySelector(".sound-button").addEventListener("click", () => {
    // Nút "Nghe" đọc từ đang xem.
    speakWord(word.hanzi, word.audio_url);
  });

  detail.querySelectorAll(".sentence-sound").forEach((button) => {
    button.addEventListener("click", () => speakWord(button.dataset.speakValue, button.dataset.audioUrl));
  });

  detail.querySelector(".show-more-examples")?.addEventListener("click", () => renderWordDetail(card, true));

  detail.querySelectorAll(".radical-link").forEach((button) => {
    button.addEventListener("click", async () => {
      await switchMode("radicals");
      selectRadical(button.dataset.radicalId);
    });
  });
}

async function loadVocabulary() {
  // Gọi API module 1: lấy các thẻ học từ vựng theo lesson_order.
  const list = document.querySelector("#wordList");
  const detail = document.querySelector("#wordDetail");
  selectedWordId = "";
  list.innerHTML = '<div class="empty-state">Đang tải từ vựng...</div>';
  detail.innerHTML = "Chọn một từ vựng để học.";
  const response = await fetch(`/api/study/vocabulary?lesson_order=${selectedLesson}`);
  vocabularyCards = await response.json();
  renderWordList(vocabularyCards);
  if (vocabularyCards.length) {
    renderWordDetail(vocabularyCards[0]);
  }
}

function renderRadicalList(radicals) {
  // Hiện danh sách bộ thủ ở module "Bộ thủ".
  const list = document.querySelector("#radicalList");
  if (!radicals.length) {
    list.innerHTML = '<div class="empty-state">Chưa có dữ liệu bộ thủ.</div>';
    return;
  }
  list.innerHTML = radicals
    .map(
      (radical) => `
        <button class="radical-item" data-radical-id="${escapeHtml(radical.id)}" type="button">
          <span class="radical-symbol">${escapeHtml(radical.radical)}</span>
          <strong>${escapeHtml(radical.han_viet || radical.pinyin || radical.meaning_vi)}</strong>
          <span>${escapeHtml(radical.pinyin)} · ${escapeHtml(radical.meaning_vi)}</span>
        </button>
      `,
    )
    .join("");

  list.querySelectorAll(".radical-item").forEach((button) => {
    button.addEventListener("click", () => selectRadical(button.dataset.radicalId));
  });
}

function renderRadicalDetail(radical) {
  // Hiện nội dung kiến thức của 1 bộ thủ.
  const detail = document.querySelector("#radicalDetail");
  const variants = radical.variants?.length
    ? radical.variants.map((item) => `<span>${escapeHtml(item)}</span>`).join("")
    : "<span>Chưa có biến thể</span>";
  const commonWords = radical.common_words?.length
    ? radical.common_words.map((item) => `<span>${escapeHtml(item)}</span>`).join("")
    : "<span>Chưa có từ ví dụ</span>";

  detail.innerHTML = `
    <div class="radical-detail-card">
      <div class="radical-detail-head">
        <div>
          <div class="radical-big">${escapeHtml(radical.radical)}</div>
          <p>${escapeHtml(radical.han_viet)} · ${escapeHtml(radical.pinyin)} · ${escapeHtml(radical.meaning_vi)}</p>
        </div>
      </div>
      <section>
        <h3>Cách nhớ</h3>
        <p>${escapeHtml(radical.memory_tip || "Chưa có cách nhớ.")}</p>
      </section>
      <section>
        <h3>Ý nghĩa bộ</h3>
        <p>${escapeHtml(radical.semantic_note || "Chưa có ghi chú ý nghĩa.")}</p>
      </section>
      <section>
        <h3>Biến thể</h3>
        <div class="tag-list">${variants}</div>
      </section>
      <section>
        <h3>Từ thường gặp</h3>
        <div class="tag-list">${commonWords}</div>
      </section>
    </div>
  `;
}

function selectRadical(radicalId) {
  // Chọn bộ thủ theo id, cập nhật nút active và nội dung chi tiết.
  const radical = radicalCards.find((item) => item.id === radicalId) || radicalCards[0];
  if (!radical) {
    return;
  }
  document.querySelectorAll(".radical-item").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.radicalId === radical.id);
  });
  renderRadicalDetail(radical);
}

async function loadRadicals() {
  // Gọi API lấy toàn bộ kiến thức bộ thủ từ kho dữ liệu hiện tại.
  const list = document.querySelector("#radicalList");
  const detail = document.querySelector("#radicalDetail");
  list.innerHTML = '<div class="empty-state">Đang tải bộ thủ...</div>';
  detail.innerHTML = "Chọn một bộ thủ để học.";
  const response = await fetch("/api/radicals");
  radicalCards = await response.json();
  renderRadicalList(radicalCards);
  if (radicalCards.length) {
    selectRadical(radicalCards[0].id);
  }
}

function renderGrammarList(grammarPoints) {
  // Hiện danh sách điểm ngữ pháp của bài đang chọn.
  const list = document.querySelector("#grammarList");
  if (!grammarPoints.length) {
    list.innerHTML = '<div class="empty-state">Chưa có ngữ pháp cho bài này.</div>';
    return;
  }
  list.innerHTML = grammarPoints
    .map(
      (grammarPoint, index) => `
        <button class="grammar-item" data-grammar-index="${index}" type="button">
          <strong>${escapeHtml(grammarPoint.title_vi)}</strong>
          <span>${escapeHtml(grammarPoint.pattern || "Chưa có công thức")}</span>
        </button>
      `,
    )
    .join("");

  list.querySelectorAll(".grammar-item").forEach((button) => {
    button.addEventListener("click", () => selectGrammar(Number(button.dataset.grammarIndex)));
  });
}

function renderGrammarDetail(grammarPoint) {
  // Hiện chi tiết một điểm ngữ pháp: công thức, giải thích, ví dụ, tags.
  const detail = document.querySelector("#grammarDetail");
  const tags = grammarPoint.tags?.length
    ? grammarPoint.tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join("")
    : "<span>Chưa có tag</span>";

  detail.innerHTML = `
    <div class="grammar-detail-card">
      <section>
        <h3>${escapeHtml(grammarPoint.title_vi)}</h3>
        <div class="grammar-pattern">${escapeHtml(grammarPoint.pattern || "Chưa có công thức.")}</div>
      </section>
      <section>
        <h3>Giải thích</h3>
        <p>${escapeHtml(grammarPoint.explanation_vi || "Chưa có giải thích.")}</p>
      </section>
      <section>
        <h3>Ví dụ</h3>
        <div class="grammar-example">
          <div class="example-head">
            <strong>${escapeHtml(grammarPoint.example_hanzi || "Chưa có ví dụ.")}</strong>
            ${
              grammarPoint.example_hanzi
                ? `<button class="sentence-sound" data-speak-value="${escapeHtml(grammarPoint.example_hanzi)}" data-audio-url="" type="button">Nghe câu</button>`
                : ""
            }
          </div>
          <span>${escapeHtml(grammarPoint.example_pinyin || "")}</span>
          <em>${escapeHtml(grammarPoint.example_vi || "")}</em>
        </div>
      </section>
      <section>
        <h3>Tags</h3>
        <div class="tag-list">${tags}</div>
      </section>
    </div>
  `;

  detail.querySelectorAll(".sentence-sound").forEach((button) => {
    button.addEventListener("click", () => speakWord(button.dataset.speakValue, button.dataset.audioUrl));
  });
}

function selectGrammar(grammarIndex) {
  // Chọn một điểm ngữ pháp trong danh sách và tô active.
  const grammarPoint = grammarCards[grammarIndex] || grammarCards[0];
  if (!grammarPoint) {
    return;
  }
  document.querySelectorAll(".grammar-item").forEach((button) => {
    button.classList.toggle("is-active", Number(button.dataset.grammarIndex) === grammarCards.indexOf(grammarPoint));
  });
  renderGrammarDetail(grammarPoint);
}

async function loadGrammar() {
  // Gọi API lấy ngữ pháp của bài đang chọn.
  const list = document.querySelector("#grammarList");
  const detail = document.querySelector("#grammarDetail");
  list.innerHTML = '<div class="empty-state">Đang tải ngữ pháp...</div>';
  detail.innerHTML = "Chọn một điểm ngữ pháp để học.";
  const response = await fetch(`/api/grammar?lesson_order=${selectedLesson}`);
  grammarCards = await response.json();
  renderGrammarList(grammarCards);
  if (grammarCards.length) {
    selectGrammar(0);
  }
}

document.querySelectorAll(".lesson").forEach((button) => {
  button.addEventListener("click", async () => {
    // Đổi bài học: tải lại từ vựng và câu hỏi game theo bài mới.
    document.querySelectorAll(".lesson").forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    selectedLesson = button.dataset.lesson;
    currentQuestionIndex = 0;
    score = 0;
    currentQuestion = null;
    const activeMode = document.querySelector(".mode.is-active")?.dataset.mode;
    await loadVocabulary();
    if (activeMode === "grammar") {
      await loadGrammar();
    }
    if (activeMode === "game") {
      await loadQuestion();
    }
  });
});

document.querySelectorAll(".game").forEach((button) => {
  button.addEventListener("click", async () => {
    // Đổi loại game: tạo lại câu hỏi game.
    document.querySelectorAll(".game").forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    selectedGame = button.dataset.game;
    currentQuestionIndex = 0;
    score = 0;
    await loadQuestion();
  });
});

document.querySelectorAll(".mode").forEach((button) => {
  button.addEventListener("click", async () => {
    // Chuyển qua lại giữa các module: Học từ vựng, Bộ thủ, Ngữ pháp, Game luyện tập.
    await switchMode(button.dataset.mode);
  });
});

document.querySelector("#syncButton").addEventListener("click", async () => {
  // Đồng bộ dữ liệu: backend sẽ thử đọc Google Sheet, nếu fail thì đọc snapshot local.
  const detail = document.querySelector("#wordDetail");
  detail.innerHTML = "Đang đồng bộ...";
  const response = await fetch("/api/sync", { method: "POST" });
  const data = await response.json();
  detail.innerHTML = `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
  currentQuestion = null;
  radicalCards = [];
  grammarCards = [];
  await loadVocabulary();
});

document.querySelector("#userSelect").addEventListener("change", async (event) => {
  // Đổi hồ sơ người học thì tải tiến độ riêng của người đó.
  await loadProgressForUser(event.target.value);
});

document.querySelector("#addUser").addEventListener("click", async () => {
  // Tạo thêm người học mới nếu lớp có hơn 10 người.
  const input = document.querySelector("#newUserName");
  const name = input.value.trim();
  if (!name) {
    return;
  }
  const response = await fetch("/api/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const user = await response.json();
  users.push(user);
  selectedUserId = user.id;
  input.value = "";
  renderUsers();
  await loadProgressForUser(selectedUserId);
});

document.querySelector("#resetProgress").addEventListener("click", async () => {
  // Xóa tiến độ học của người đang chọn, không ảnh hưởng dữ liệu bài học.
  try {
    const response = await fetch(`/api/users/${selectedUserId}/progress/reset`, { method: "POST" });
    currentProgress = await response.json();
  } catch {
    currentProgress = emptyProgress();
  }
  localStorage.setItem(progressStorageKey, JSON.stringify(currentProgress));
  renderProgress();
});

async function initApp() {
  // Khởi động frontend: tải người học trước, rồi mới tải dữ liệu học.
  await loadUsers();
  await loadVocabulary();
}

initApp();
