from datetime import datetime
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")
MAX_ENTRIES = 10


def _ensure_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_leaderboard() -> list[dict]:
    _ensure_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_leaderboard(entries: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries[:MAX_ENTRIES], f, ensure_ascii=False, indent=2)


def add_record(
    player_name: str,
    score: int,
    steps: int,
    elapsed_seconds: int,
    mode_label: str,
) -> list[dict]:
    clean_name = (player_name or "").strip()[:20] or "Anonymous Detective"
    entries = load_leaderboard()

    entries.append(
        {
            "name": clean_name,
            "score": int(score),
            "steps": int(steps),
            "elapsed_seconds": int(elapsed_seconds),
            "mode": mode_label,
            "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )

    entries.sort(key=lambda item: (-item["score"], item["elapsed_seconds"], item["steps"]))
    trimmed = entries[:MAX_ENTRIES]
    save_leaderboard(trimmed)
    return trimmed