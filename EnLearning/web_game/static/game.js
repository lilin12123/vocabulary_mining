const state = {
  session: null,
  stepIndex: 0,
  hp: 3,
  score: 0,
  combo: 0,
  maxCombo: 0,
  correctCount: 0,
  total: 10,
  mapSize: 5,
  tiles: [],
  position: 0,
  visited: new Set(),
  inQuestion: false,
  eliteMode: false,
  tileMessage: "",
  items: {
    eliminate: 1,
    heal: 0,
    pos: 1,
  },
  usedEliminate: false,
  showPosHint: false,
  token: null,
  username: null,
};

const ui = {
  bookSelect: document.getElementById("book-select"),
  startBtn: document.getElementById("start-btn"),
  enterMapBtn: document.getElementById("enter-map-btn"),
  difficultySelect: document.getElementById("difficulty-select"),
  viewBookBtn: document.getElementById("view-book-btn"),
  usernameInput: document.getElementById("username-input"),
  passwordInput: document.getElementById("password-input"),
  registerBtn: document.getElementById("register-btn"),
  loginBtn: document.getElementById("login-btn"),
  loginStatus: document.getElementById("login-status"),
  previewPanel: document.getElementById("preview-panel"),
  previewList: document.getElementById("preview-list"),
  gamePanel: document.getElementById("game-panel"),
  resultPanel: document.getElementById("result-panel"),
  historyPanel: document.getElementById("history-panel"),
  historyList: document.getElementById("history-list"),
  leaderboardList: document.getElementById("leaderboard-list"),
  statsList: document.getElementById("stats-list"),
  stepCount: document.getElementById("step-count"),
  stepTotal: document.getElementById("step-total"),
  hpCount: document.getElementById("hp-count"),
  comboCount: document.getElementById("combo-count"),
  mapGrid: document.getElementById("map-grid"),
  moveBtn: document.getElementById("move-btn"),
  wordTitle: document.getElementById("word-title"),
  wordPhonetic: document.getElementById("word-phonetic"),
  posHint: document.getElementById("pos-hint"),
  sentenceList: document.getElementById("sentence-list"),
  options: document.getElementById("options"),
  feedback: document.getElementById("feedback"),
  itemEliminate: document.getElementById("item-eliminate"),
  itemHeal: document.getElementById("item-heal"),
  itemPos: document.getElementById("item-pos"),
  scoreResult: document.getElementById("score-result"),
  accuracyResult: document.getElementById("accuracy-result"),
  maxComboResult: document.getElementById("max-combo-result"),
  hpResult: document.getElementById("hp-result"),
  resultSub: document.getElementById("result-sub"),
  restartBtn: document.getElementById("restart-btn"),
  toast: document.getElementById("toast"),
};

const TILE_WEIGHTS = [
  { type: "normal", weight: 0.5 },
  { type: "treasure", weight: 0.15 },
  { type: "trap", weight: 0.15 },
  { type: "elite", weight: 0.1 },
  { type: "heal", weight: 0.1 },
];

function randomTile() {
  const r = Math.random();
  let acc = 0;
  for (const item of TILE_WEIGHTS) {
    acc += item.weight;
    if (r <= acc) return item.type;
  }
  return "normal";
}

function showToast(message) {
  ui.toast.textContent = message;
  ui.toast.classList.remove("hidden");
  setTimeout(() => ui.toast.classList.add("hidden"), 1600);
}

async function fetchWordbooks() {
  const resp = await fetch("/api/wordbooks");
  const data = await resp.json();
  ui.bookSelect.innerHTML = "";
  data.books.forEach((book) => {
    const option = document.createElement("option");
    option.value = book.id;
    const tags = [];
    if (book.has_words) tags.push("words");
    if (book.has_phrases) tags.push("phrases");
    option.textContent = `${book.id} (${tags.join("+")})`;
    ui.bookSelect.appendChild(option);
  });
}

function getDifficultyCount() {
  const value = ui.difficultySelect.value;
  if (value === "medium") return 20;
  if (value === "hard") return 30;
  return 10;
}

async function preloadSession() {
  const bookId = ui.bookSelect.value;
  const count = getDifficultyCount();
  ui.startBtn.disabled = true;
  ui.startBtn.textContent = "生成中...";
  const resp = await fetch("/api/preload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ book_id: bookId, count, token: state.token }),
  });
  if (!resp.ok) {
    const error = await resp.json();
    ui.startBtn.disabled = false;
    ui.startBtn.textContent = "开始关卡";
    alert(error.detail || "加载失败");
    return;
  }
  const data = await resp.json();
  state.session = data;
  state.total = data.count;
  ui.startBtn.disabled = false;
  ui.startBtn.textContent = "开始关卡";
  renderPreview(data.words);
  ui.previewPanel.classList.remove("hidden");
  ui.gamePanel.classList.add("hidden");
  ui.resultPanel.classList.add("hidden");
}

function renderPreview(words) {
  ui.previewList.innerHTML = "";
  words.forEach((w, idx) => {
    const card = document.createElement("div");
    card.className = "preview-item";
    card.innerHTML = `
      <h4>${idx + 1}. ${w.word} <span>${w.phonetic || ""}</span></h4>
      <span class="muted">${w.type === "phrase" ? "短语" : "单词"}</span>
      <div>${w.meaning}</div>
      <span>${w.example}</span>
    `;
    ui.previewList.appendChild(card);
  });
}

function generateMap(size) {
  const tiles = Array.from({ length: size * size }, () => randomTile());
  return tiles;
}

function getNeighbors(index, size) {
  const row = Math.floor(index / size);
  const col = index % size;
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ]
    .filter(([r, c]) => r >= 0 && r < size && c >= 0 && c < size)
    .map(([r, c]) => r * size + c);
}

function renderMap() {
  ui.mapGrid.innerHTML = "";
  const size = state.mapSize;
  ui.mapGrid.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
  for (let i = 0; i < size * size; i++) {
    const cell = document.createElement("div");
    cell.className = "map-cell";
    if (state.visited.has(i)) {
      cell.classList.add("visited");
      cell.classList.add(state.tiles[i]);
    }
    if (state.position === i) {
      cell.classList.add("current");
    }
    const neighbors = getNeighbors(state.position, size);
    if (!state.inQuestion && neighbors.includes(i)) {
      cell.classList.add("neighbor");
      cell.addEventListener("click", () => moveTo(i));
    }
    ui.mapGrid.appendChild(cell);
  }
}

function moveTo(index) {
  if (state.inQuestion) return;
  const firstVisit = !state.visited.has(index);
  state.position = index;
  state.visited.add(index);
  state.eliteMode = false;
  state.tileMessage = "";

  const tile = state.tiles[index];
  if (firstVisit) {
    if (tile === "trap") {
      state.hp -= 1;
      state.tileMessage = "触发陷阱：生命 -1";
    } else if (tile === "treasure") {
      const reward = rewardItem();
      state.tileMessage = `宝箱奖励：${reward}`;
    } else if (tile === "heal") {
      state.hp = Math.min(5, state.hp + 1);
      state.tileMessage = "治疗泉：生命 +1";
    } else if (tile === "elite") {
      state.eliteMode = true;
      state.tileMessage = "精英格：答错额外扣血，答对额外加分";
    }
  }

  renderMap();
  if (state.hp <= 0) {
    endGame(false);
    return;
  }
  state.inQuestion = true;
  renderQuestion();
  ui.moveBtn.disabled = true;
}

function resetStats() {
  state.stepIndex = 0;
  state.hp = 3;
  state.score = 0;
  state.combo = 0;
  state.maxCombo = 0;
  state.correctCount = 0;
  state.items = { eliminate: 1, heal: 0, pos: 1 };
  state.usedEliminate = false;
  state.showPosHint = false;
  state.mapSize = state.total <= 25 ? 5 : 6;
  state.tiles = generateMap(state.mapSize);
  state.position = Math.floor(Math.random() * state.mapSize * state.mapSize);
  state.tiles[state.position] = "normal";
  state.visited = new Set([state.position]);
  state.inQuestion = false;
  state.eliteMode = false;
}

function updateStats() {
  const displayedStep = Math.min(state.stepIndex + (state.inQuestion ? 1 : 0), state.total);
  ui.stepCount.textContent = displayedStep;
  ui.stepTotal.textContent = state.total;
  ui.hpCount.textContent = state.hp;
  ui.comboCount.textContent = state.combo;
  ui.itemEliminate.querySelector("span").textContent = state.items.eliminate;
  ui.itemHeal.querySelector("span").textContent = state.items.heal;
  ui.itemPos.querySelector("span").textContent = state.items.pos;
  const lockItems = !state.inQuestion;
  ui.itemEliminate.disabled = lockItems || state.items.eliminate <= 0 || state.usedEliminate;
  ui.itemHeal.disabled = lockItems || state.items.heal <= 0 || state.hp >= 5;
  ui.itemPos.disabled = lockItems || state.items.pos <= 0 || state.showPosHint;
}

function renderQuestion() {
  const q = state.session.questions[state.stepIndex];
  ui.wordTitle.textContent = q.word;
  ui.wordPhonetic.textContent = q.phonetic || "";
  ui.posHint.textContent = state.showPosHint ? q.pos : "???";

  ui.sentenceList.innerHTML = "";
  q.sentences.forEach((s) => {
    const div = document.createElement("div");
    div.className = "sentence";
    div.textContent = s;
    ui.sentenceList.appendChild(div);
  });

  ui.options.innerHTML = "";
  q.options.forEach((opt) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.textContent = opt.text;
    btn.dataset.correct = opt.correct ? "1" : "0";
    btn.addEventListener("click", () => handleAnswer(btn, opt.correct));
    ui.options.appendChild(btn);
  });

  ui.feedback.textContent = state.tileMessage || "";
  state.usedEliminate = false;
  state.showPosHint = false;
  updateStats();
}

function handleAnswer(button, correct) {
  const buttons = ui.options.querySelectorAll("button");
  buttons.forEach((btn) => (btn.disabled = true));

  if (correct) {
    button.classList.add("correct");
    state.combo += 1;
    state.maxCombo = Math.max(state.maxCombo, state.combo);
    state.correctCount += 1;
    const multiplier = 1 + Math.min(state.combo - 1, 4) * 0.2;
    const eliteBonus = state.eliteMode ? 5 : 0;
    state.score += Math.round(10 * multiplier) + eliteBonus;
    ui.feedback.textContent = `答对！连击 x${state.combo}`;

    if (state.correctCount % 3 === 0) {
      const reward = rewardItem();
      showToast(`获得道具：${reward}`);
    }
  } else {
    button.classList.add("wrong");
    buttons.forEach((btn) => {
      if (btn.dataset.correct === "1") {
        btn.classList.add("correct");
      }
    });
    state.hp -= state.eliteMode ? 2 : 1;
    state.combo = 0;
    ui.feedback.textContent = state.eliteMode ? "答错了，生命 -2" : "答错了，生命 -1";
  }

  updateStats();
  state.inQuestion = false;
  state.eliteMode = false;
  state.tileMessage = "";
  state.stepIndex += 1;
  ui.moveBtn.disabled = false;
  if (state.hp <= 0) {
    endGame(false);
    return;
  }
  if (state.stepIndex >= state.session.questions.length) {
    endGame(true);
    return;
  }
  renderMap();
}

function rewardItem() {
  const pool = ["移除干扰项", "生命+1", "词性提示"];
  const reward = pool[Math.floor(Math.random() * pool.length)];
  if (reward === "移除干扰项") state.items.eliminate += 1;
  if (reward === "生命+1") state.items.heal += 1;
  if (reward === "词性提示") state.items.pos += 1;
  updateStats();
  return reward;
}

function endGame(success) {
  ui.gamePanel.classList.add("hidden");
  ui.resultPanel.classList.remove("hidden");
  const accuracy = Math.round((state.correctCount / state.session.questions.length) * 100);
  ui.scoreResult.textContent = state.score;
  ui.accuracyResult.textContent = `${accuracy}%`;
  ui.maxComboResult.textContent = state.maxCombo;
  ui.hpResult.textContent = state.hp;
  ui.resultSub.textContent = success ? "挑战完成！" : "生命耗尽，关卡失败。";

  if (state.token) {
    fetch("/api/record", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: state.token,
        book_id: state.session.book_id,
        difficulty: ui.difficultySelect.value,
        score: state.score,
        accuracy,
        max_combo: state.maxCombo,
        hp_left: state.hp,
        total: state.session.questions.length,
      }),
    })
      .then(fetchRecords)
      .then(fetchLeaderboard)
      .then(fetchStats);
  } else {
    fetchLeaderboard();
    fetchStats();
  }
}

ui.startBtn.addEventListener("click", preloadSession);
ui.enterMapBtn.addEventListener("click", () => {
  ui.previewPanel.classList.add("hidden");
  ui.gamePanel.classList.remove("hidden");
  ui.resultPanel.classList.add("hidden");
  resetStats();
  renderMap();
  ui.moveBtn.disabled = false;
});

ui.moveBtn.addEventListener("click", () => {
  if (state.inQuestion) return;
  const neighbors = getNeighbors(state.position, state.mapSize).filter((n) => !state.visited.has(n));
  if (!neighbors.length) {
    showToast("没有可前进的格子");
    return;
  }
  const next = neighbors[Math.floor(Math.random() * neighbors.length)];
  moveTo(next);
});

ui.itemEliminate.addEventListener("click", () => {
  if (state.items.eliminate <= 0 || state.usedEliminate) return;
  const wrongOptions = Array.from(ui.options.querySelectorAll("button")).filter(
    (btn) => btn.dataset.correct === "0" && btn.style.display !== "none"
  );
  if (wrongOptions.length) {
    wrongOptions[0].style.display = "none";
    state.items.eliminate -= 1;
    state.usedEliminate = true;
    updateStats();
  }
});

ui.itemHeal.addEventListener("click", () => {
  if (state.items.heal <= 0 || state.hp >= 5) return;
  state.items.heal -= 1;
  state.hp += 1;
  updateStats();
  showToast("生命 +1");
});

ui.itemPos.addEventListener("click", () => {
  if (state.items.pos <= 0 || state.showPosHint) return;
  state.items.pos -= 1;
  state.showPosHint = true;
  ui.posHint.textContent = state.session.questions[state.stepIndex].pos || "unknown";
  updateStats();
});

ui.restartBtn.addEventListener("click", () => {
  ui.resultPanel.classList.add("hidden");
  ui.previewPanel.classList.remove("hidden");
});

async function registerUser() {
  const username = ui.usernameInput.value.trim();
  const password = ui.passwordInput.value.trim();
  if (!username || !password) {
    showToast("请输入用户名和密码");
    return;
  }
  const resp = await fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) {
    const err = await resp.json();
    showToast(err.detail || "注册失败");
    return;
  }
  showToast("注册成功，请登录");
}

async function loginUser() {
  const username = ui.usernameInput.value.trim();
  const password = ui.passwordInput.value.trim();
  if (!username || !password) {
    showToast("请输入用户名和密码");
    return;
  }
  const resp = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!resp.ok) {
    const err = await resp.json();
    showToast(err.detail || "登录失败");
    return;
  }
  const data = await resp.json();
  state.token = data.token;
  state.username = data.username;
  localStorage.setItem("vocab_token", state.token);
  localStorage.setItem("vocab_username", state.username);
  updateLoginStatus();
  fetchRecords();
  fetchStats();
}

function updateLoginStatus() {
  if (state.username) {
    ui.loginStatus.textContent = `已登录：${state.username}`;
    ui.historyPanel.classList.remove("hidden");
  } else {
    ui.loginStatus.textContent = "未登录";
    ui.historyPanel.classList.add("hidden");
  }
}

async function fetchRecords() {
  if (!state.token) return;
  const resp = await fetch(`/api/records?token=${state.token}`);
  if (!resp.ok) return;
  const data = await resp.json();
  ui.historyList.innerHTML = "";
  data.records.slice().reverse().forEach((r) => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div>日期：${new Date(r.timestamp).toLocaleString()}</div>
      <div>词库：${r.book_id} · 难度：${r.difficulty}</div>
      <div>得分：${r.score} · 准确率：${r.accuracy}% · 最高连击：${r.max_combo}</div>
      <div>剩余HP：${r.hp_left} · 题数：${r.total}</div>
    `;
    ui.historyList.appendChild(div);
  });
}

async function fetchLeaderboard() {
  const difficulty = ui.difficultySelect.value;
  const resp = await fetch(`/api/leaderboard?difficulty=${difficulty}`);
  if (!resp.ok) return;
  const data = await resp.json();
  ui.leaderboardList.innerHTML = "";
  if (!data.rows.length) {
    ui.leaderboardList.innerHTML = "<div class=\"history-item\">暂无记录</div>";
    return;
  }
  data.rows.forEach((r, idx) => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div>#${idx + 1} ${r.username}</div>
      <div>得分：${r.score} · 准确率：${r.accuracy}% · 难度：${r.difficulty}</div>
      <div>词库：${r.book_id} · 时间：${new Date(r.timestamp).toLocaleString()}</div>
    `;
    ui.leaderboardList.appendChild(div);
  });
}

async function fetchStats() {
  const url = state.token ? `/api/stats?token=${state.token}` : "/api/stats";
  const resp = await fetch(url);
  if (!resp.ok) return;
  const data = await resp.json();
  ui.statsList.innerHTML = "";
  const global = data.global;
  ui.statsList.innerHTML += `
    <div class="history-item">
      <div>全站用户：${global.total_users} · 总局数：${global.total_games}</div>
      <div>平均得分：${global.avg_score} · 平均准确率：${global.avg_accuracy}%</div>
      <div>最高得分：${global.best_score} · 最高准确率：${global.best_accuracy}%</div>
    </div>
  `;
  if (data.user) {
    const u = data.user;
    ui.statsList.innerHTML += `
      <div class="history-item">
        <div>账号：${data.username}</div>
        <div>总局数：${u.total_games} · 平均得分：${u.avg_score}</div>
        <div>平均准确率：${u.avg_accuracy}% · 最高得分：${u.best_score}</div>
        <div>最高准确率：${u.best_accuracy}%</div>
      </div>
    `;
  }
}

ui.registerBtn.addEventListener("click", registerUser);
ui.loginBtn.addEventListener("click", loginUser);
ui.difficultySelect.addEventListener("change", fetchLeaderboard);

ui.viewBookBtn.addEventListener("click", () => {
  const bookId = ui.bookSelect.value;
  if (bookId) {
    window.open(`/book/${bookId}`, "_blank");
  }
});

function loadSession() {
  const token = localStorage.getItem("vocab_token");
  const username = localStorage.getItem("vocab_username");
  if (token && username) {
    state.token = token;
    state.username = username;
    updateLoginStatus();
    fetchRecords();
  }
}

fetchWordbooks();
loadSession();
fetchLeaderboard();
fetchStats();

function renderGameToText() {
  const payload = {
    mode: state.inQuestion ? "question" : "move",
    step: state.stepIndex,
    total: state.total,
    hp: state.hp,
    score: state.score,
    combo: state.combo,
    position: state.position,
    map_size: state.mapSize,
    visited_count: state.visited.size,
    neighbors: getNeighbors(state.position, state.mapSize),
  };
  if (state.inQuestion && state.session) {
    const q = state.session.questions[state.stepIndex];
    payload.question = {
      word: q.word,
      options: q.options.map((o) => o.text),
    };
  }
  return JSON.stringify(payload);
}

window.render_game_to_text = renderGameToText;
window.advanceTime = () => {
  renderMap();
  updateStats();
};

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.();
  } else {
    document.exitFullscreen?.();
  }
}

document.addEventListener("keydown", (e) => {
  if (e.key === "f") {
    toggleFullscreen();
  }
  if (e.key === "Escape" && document.fullscreenElement) {
    document.exitFullscreen?.();
  }
});
