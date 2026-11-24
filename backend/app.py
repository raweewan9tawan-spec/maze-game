from flask import Flask, jsonify, request, send_from_directory
from leaderboard import add_record, load_leaderboard
from maze_logic import MazeGame
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
game = MazeGame(level_index=0)


@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/state", methods=["GET"])
def get_state():
    show_hint = request.args.get("hint", "false").lower() == "true"
    payload = game.to_dict(include_hint=show_hint)
    payload["leaderboard"] = load_leaderboard()
    return jsonify(payload)


@app.route("/api/start", methods=["POST"])
def start_session():
    body = request.get_json(silent=True) or {}
    mode = body.get("mode", "level")
    level = int(body.get("level", 0))
    size = int(body.get("size", 9))

    if mode == "random":
        game.start_game(level_index=level, random_size=size)
    else:
        game.start_game(level_index=level, random_size=None)

    payload = game.to_dict(include_hint=False)
    payload["leaderboard"] = load_leaderboard()
    return jsonify(payload)


@app.route("/api/move", methods=["POST"])
def move_player():
    body = request.get_json(silent=True) or {}
    direction = body.get("direction", "")
    result = game.move(direction)
    state = game.to_dict(include_hint=False)
    state["move_result"] = result
    state["leaderboard"] = load_leaderboard()
    return jsonify(state), (200 if result["valid"] else 400)


@app.route("/api/reset", methods=["POST"])
def reset_game():
    body = request.get_json(silent=True) or {}
    level = body.get("level")
    game.reset(level_index=level, keep_started=True)
    payload = game.to_dict(include_hint=False)
    payload["leaderboard"] = load_leaderboard()
    return jsonify(payload)


@app.route("/api/generate", methods=["POST"])
def generate_maze():
    body = request.get_json(silent=True) or {}
    size = int(body.get("size", 9))
    game.generate_new_random(size=size)
    payload = game.to_dict(include_hint=False)
    payload["leaderboard"] = load_leaderboard()
    return jsonify(payload)


@app.route("/api/leaderboard", methods=["GET", "POST"])
def leaderboard_endpoint():
    if request.method == "GET":
        return jsonify({"leaderboard": load_leaderboard()})

    body = request.get_json(silent=True) or {}
    if not game.won:
        return jsonify({"error": "ต้องเล่นจนถึงเส้นชัยก่อนจึงจะบันทึกสถิติได้"}), 400

    player_name = body.get("name", "")
    mode_label = f"Random {game.rows}×{game.cols}" if game.is_random else f"Level {game.level_index + 1}"
    updated = add_record(
        player_name=player_name,
        score=game.calculate_score(),
        steps=game.steps,
        elapsed_seconds=game.get_elapsed_seconds(),
        mode_label=mode_label,
    )
    return jsonify({"leaderboard": updated}), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)