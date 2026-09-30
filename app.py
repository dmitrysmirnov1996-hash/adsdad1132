import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/check')
def check():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "no username"}), 400

    try:
        # Ограничиваем: только 300 самых популярных сайтов, таймаут 15 сек на сайт
        result = subprocess.run(
            ["maigret", username, "--top-sites", "300", "--timeout", "15", "--json", "ndjson"],
            capture_output=True, text=True, timeout=90
        )

        found = []
        for line in result.stdout.splitlines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get("status") == "Claimed":
                        found.append(data.get("site_name", "?"))
                except json.JSONDecodeError:
                    continue

        return jsonify({
            "username": username,
            "total": len(found),
            "found": found,
            "stderr": result.stderr[-300:] if result.stderr else ""
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout", "message": "Maigret не успел за 90 секунд. Попробуй другого юзера."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return jsonify({"status": "ok", "service": "maigret-checker", "mode": "top-300-sites"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
