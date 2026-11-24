const startScreenEl = document.getElementById("start-screen");
const startModeSelectEl = document.getElementById("start-mode-select");
const startLevelGroupEl = document.getElementById("start-level-group");
const startSizeGroupEl = document.getElementById("start-size-group");
const startLevelSelectEl = document.getElementById("start-level-select");
const startSizeSelectEl = document.getElementById("start-size-select");
const startGameBtnEl = document.getElementById("start-game-btn");
const startLeaderboardBodyEl = document.getElementById("start-leaderboard-body");

const homeBtnEl = document.getElementById("home-btn");
const boardEl = document.getElementById("maze-board");
const stepsEl = document.getElementById("steps-count");
const timeEl = document.getElementById("time-display");
const scoreEl = document.getElementById("score-display");
const keyStatusEl = document.getElementById("key-status");
const statusEl = document.getElementById("status-banner");
const levelSelectEl = document.getElementById("level-select");
const resetBtnEl = document.getElementById("reset-btn");
const randomBtnEl = document.getElementById("random-btn");
const hintBtnEl = document.getElementById("hint-btn");
const toggleGuidelinesEl = document.getElementById("toggle-guidelines");
const themeButtons = document.querySelectorAll(".theme-btn");
const dirButtons = document.querySelectorAll(".btn-dir");
const saveScoreFormEl = document.getElementById("save-score-form");
const playerNameInputEl = document.getElementById("player-name-input");
const leaderboardBodyEl = document.getElementById("leaderboard-body");

let currentHintPath = [];
let currentState = null;
let timerIntervalId = null;
let scoreSavedForCurrentWin = false;
let isOnStartScreen = true;

function formatTime(totalSeconds) {
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function syncTimerDisplay() {
  if (!currentState) return;
  timeEl.textContent = formatTime(currentState.elapsed_seconds ?? 0);
  scoreEl.textContent = String(currentState.score ?? 0);
}

function startLocalTimer() {
  stopLocalTimer();
  timerIntervalId = setInterval(() => {
    if (!currentState || !currentState.started || currentState.won || isOnStartScreen) {
      stopLocalTimer();
      return;
    }
    currentState.elapsed_seconds = (currentState.elapsed_seconds ?? 0) + 1;
    currentState.score = Math.max(50, (currentState.score ?? 50) - 10);
    syncTimerDisplay();
  }, 1000);
}

function stopLocalTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderLeaderboard(entries = []) {
  if (!entries.length) {
    const emptyHtml = `<tr><td colspan="5" class="empty-row">ยังไม่มีสถิติ — เล่นให้ถึงเส้นชัยเพื่อบันทึกชื่อ!</td></tr>`;
    leaderboardBodyEl.innerHTML = emptyHtml;
    startLeaderboardBodyEl.innerHTML = emptyHtml;
    return;
  }

  const rowsHtml = entries
    .map(
      (item, idx) => `
      <tr>
        <td>${idx + 1}</td>
        <td>${escapeHtml(item.name)}</td>
        <td><strong>${item.score}</strong></td>
        <td>${formatTime(item.elapsed_seconds)}</td>
        <td>${escapeHtml(item.mode)}</td>
      </tr>
    `
    )
    .join("");

  leaderboardBodyEl.innerHTML = rowsHtml;
  startLeaderboardBodyEl.innerHTML = rowsHtml;
}

function setStartScreenVisible(visible) {
  isOnStartScreen = visible;
  startScreenEl.classList.toggle("hidden", !visible);
  if (visible) {
    stopLocalTimer();
  } else if (currentState && currentState.started && !currentState.won) {
    startLocalTimer();
  }
}

function renderBoard(state) {
  currentState = state;
  const { started, rows, cols, grid, player, goal, steps, has_key, won, status, level, leaderboard } = state;

  boardEl.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  boardEl.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  boardEl.innerHTML = "";

  const hintSet = new Set(currentHintPath.map(([r, c]) => `${r},${c}`));

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");

      const code = grid[r][c];
      if (code === 1) {
        cell.classList.add("cell-wall");
      } else {
        cell.classList.add("cell-path");
      }

      if (code === 4) {
        cell.classList.add("cell-key");
        cell.textContent = "🔑";
      } else if (code === 5) {
        cell.classList.add("cell-door");
        cell.textContent = "🔒";
      }

      const isGoal = r === goal.row && c === goal.col;
      const isPlayer = r === player.row && c === player.col;

      if (isGoal) {
        cell.classList.add("cell-goal");
        cell.textContent = "★";
      }

      if (hintSet.has(`${r},${c}`) && !isPlayer && !isGoal && code !== 4 && code !== 5) {
        cell.classList.add("cell-hint");
      }

      if (isPlayer) {
        cell.classList.add("cell-player");
        cell.textContent = "●";
      }

      const coordTag = document.createElement("span");
      coordTag.className = "coord-tag";
      coordTag.textContent = `${r + 1},${c + 1}`;
      cell.appendChild(coordTag);

      boardEl.appendChild(cell);
    }
  }

  levelSelectEl.value = String(level - 1);
  stepsEl.textContent = String(steps);
  keyStatusEl.textContent = has_key ? "มีกุญแจ (1)" : "ยังไม่มี";
  syncTimerDisplay();

  if (leaderboard) {
    renderLeaderboard(leaderboard);
  }

  if (won) {
    stopLocalTimer();
    if (!scoreSavedForCurrentWin) {
      saveScoreFormEl.classList.remove("hidden");
      playerNameInputEl.focus();
    }
  } else {
    scoreSavedForCurrentWin = false;
    saveScoreFormEl.classList.add("hidden");
    if (started && !isOnStartScreen) {
      startLocalTimer();
    }
  }

  statusEl.textContent = status;
  statusEl.classList.remove("is-error", "is-won");
  if (won) {
    statusEl.classList.add("is-won");
  } else if (state.move_result && !state.move_result.valid) {
    statusEl.classList.add("is-error");
  }
}

async function handleStartGame() {
  const mode = startModeSelectEl.value;
  const level = Number(startLevelSelectEl.value);
  const size = Number(startSizeSelectEl.value);

  currentHintPath = [];
  scoreSavedForCurrentWin = false;
  const state = await MazeAPI.startGame({ mode, level, size });
  setStartScreenVisible(false);
  renderBoard(state);
}

async function handleMove(direction) {
  if (isOnStartScreen || document.activeElement === playerNameInputEl) return;
  currentHintPath = [];
  const state = await MazeAPI.sendMove(direction);
  if (state.status) {
    renderBoard(state);
  }
}

async function handleReset(levelIndex = null) {
  currentHintPath = [];
  scoreSavedForCurrentWin = false;
  const state = await MazeAPI.resetLevel(levelIndex);
  renderBoard(state);
}

async function handleRandomMaze() {
  currentHintPath = [];
  scoreSavedForCurrentWin = false;
  const size = Number(startSizeSelectEl.value) || 9;
  const state = await MazeAPI.generateRandomMaze(size);
  renderBoard(state);
}

async function handleShowHint() {
  const state = await MazeAPI.fetchState(true);
  currentHintPath = state.hint_path || [];
  renderBoard(state);
  statusEl.classList.remove("is-error", "is-won");
  statusEl.textContent = `Python BFS คำนวณเส้นทางสั้นสุดได้ ${Math.max(0, currentHintPath.length - 1)} ก้าว`;
}

startModeSelectEl.addEventListener("change", (e) => {
  const isRandom = e.target.value === "random";
  startLevelGroupEl.classList.toggle("hidden", isRandom);
  startSizeGroupEl.classList.toggle("hidden", !isRandom);
});

startGameBtnEl.addEventListener("click", handleStartGame);
homeBtnEl.addEventListener("click", () => setStartScreenVisible(true));

saveScoreFormEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = playerNameInputEl.value.trim();
  if (!name) return;

  const res = await MazeAPI.submitScore(name);
  if (res.leaderboard) {
    scoreSavedForCurrentWin = true;
    saveScoreFormEl.classList.add("hidden");
    playerNameInputEl.value = "";
    renderLeaderboard(res.leaderboard);
    statusEl.textContent = `บันทึกสถิติของ "${name}" ลง Leaderboard เรียบร้อยแล้ว!`;
  }
});

dirButtons.forEach((btn) => {
  btn.addEventListener("click", () => handleMove(btn.dataset.dir));
});

document.addEventListener("keydown", (e) => {
  if (isOnStartScreen || document.activeElement === playerNameInputEl) return;
  const keyMap = {
    ArrowUp: "UP",
    w: "UP",
    W: "UP",
    ArrowDown: "DOWN",
    s: "DOWN",
    S: "DOWN",
    ArrowLeft: "LEFT",
    a: "LEFT",
    A: "LEFT",
    ArrowRight: "RIGHT",
    d: "RIGHT",
    D: "RIGHT",
  };
  if (keyMap[e.key]) {
    e.preventDefault();
    handleMove(keyMap[e.key]);
  }
});

levelSelectEl.addEventListener("change", (e) => {
  handleReset(Number(e.target.value));
});

resetBtnEl.addEventListener("click", () => {
  handleReset(Number(levelSelectEl.value));
});

randomBtnEl.addEventListener("click", handleRandomMaze);
hintBtnEl.addEventListener("click", handleShowHint);

toggleGuidelinesEl.addEventListener("change", (e) => {
  boardEl.classList.toggle("show-guidelines", e.target.checked);
});

themeButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    document.body.classList.remove("theme-indigo", "theme-forest", "theme-sunset");
    document.body.classList.add(btn.dataset.theme);
    themeButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

(async function init() {
  const initialState = await MazeAPI.fetchState(false);
  renderBoard(initialState);
  setStartScreenVisible(!initialState.started);
})();