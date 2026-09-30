import os
import json
import concurrent.futures
import urllib.request
import urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

# Официальная база Sherlock (400+ сайтов, MIT license)
SHERLOCK_DATA_URL = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json"

# Кэш базы
_sherlock_cache = None


def _load_sherlock_data():
    """Загружает официальную базу Sherlock."""
    global _sherlock_cache
    if _sherlock_cache is not None:
        return _sherlock_cache

    try:
        req = urllib.request.Request(
            SHERLOCK_DATA_URL,
            headers={"User-Agent": "SherlockLike/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        _sherlock_cache = data
        return data
    except Exception as e:
        print(f"[sherlock load error] {e}")
        return {}


def _check_site(site_name, site_data, username):
    """
    Проверяет один сайт по правилам Sherlock.
    Sherlock использует:
    - url: шаблон URL с {username}
    - urlMain: главная страница
    - errorType: тип проверки (status_code / message)
    - errorMsg: сообщение об ошибке (если errorType=message)
    """
    try:
        url_template = site_data.get("url", "")
        if not url_template:
            return None

        url = url_template.format(username=username)

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                status = resp.getcode()
                body = resp.read(5000).decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            status = e.code
            body = ""
        except Exception:
            return None

        # Проверка по правилам Sherlock
        error_type = site_data.get("errorType", "status_code")

        if error_type == "status_code":
            # Если 200 — аккаунт существует
            if status == 200:
                # Проверяем errorMsg для дополнительной фильтрации
                error_msg = site_data.get("errorMsg", "")
                if error_msg and error_msg in body:
                    return None
                return {"site": site_name, "url": url, "status": status}

        elif error_type == "message":
            # Проверяем, нет ли сообщения об ошибке на странице
            error_msg = site_data.get("errorMsg", "")
            if status == 200:
                if error_msg and error_msg in body:
                    return None
                return {"site": site_name, "url": url, "status": status}

        return None

    except Exception:
        return None


@app.route('/')
def index():
    data = _load_sherlock_data()
    return jsonify({
        "status": "ok",
        "service": "sherlock-like",
        "sites_loaded": len(data),
        "source": "sherlock-project/sherlock (MIT)"
    })


@app.route('/check')
def check():
    """Проверяет username по всем сайтам из базы Sherlock."""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "no username"}), 400

    data = _load_sherlock_data()
    if not data:
        return jsonify({"error": "sherlock data not loaded"}), 500

    found = []

    # Параллельная проверка (30 потоков)
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = {
            executor.submit(_check_site, name, info, username): name
            for name, info in data.items()
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found.append(result)

    # Сортируем по алфавиту
    found.sort(key=lambda x: x["site"].lower())

    return jsonify({
        "username": username,
        "total": len(found),
        "sites_checked": len(data),
        "found": [f["site"] for f in found],
        "urls": {f["site"]: f["url"] for f in found}
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
