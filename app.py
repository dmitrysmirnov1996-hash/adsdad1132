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

    # Запускаем официальный Docker-образ Maigret
    # Флаг -a ищет по всем сайтам, --json ndjson выводит результат в формате JSON
    cmd = [
        "docker", "run", "--rm", "soxoj/maigret:latest",
        username, "-a", "--json", "ndjson"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        found = []
        for line in result.stdout.splitlines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get("status") == "Claimed":
                        found.append(data.get("site_name", "?"))
                except json.JSONDecodeError:
                    continue

        return jsonify({"username": username, "total": len(found), "found": found})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
