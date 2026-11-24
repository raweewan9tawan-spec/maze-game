const MazeAPI = {
  async fetchState(includeHint = false) {
    const query = includeHint ? "?hint=true" : "";
    const res = await fetch(`/api/state${query}`);
    return res.json();
  },

  async startGame(options = {}) {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options),
    });
    return res.json();
  },

  async sendMove(direction) {
    const res = await fetch("/api/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ direction }),
    });
    return res.json();
  },

  async resetLevel(levelIndex = null) {
    const res = await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(levelIndex !== null ? { level: levelIndex } : {}),
    });
    return res.json();
  },

  async generateRandomMaze(size = 9) {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ size }),
    });
    return res.json();
  },

  async submitScore(name) {
    const res = await fetch("/api/leaderboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    return res.json();
  },
};