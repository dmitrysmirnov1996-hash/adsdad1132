import os
import json
import concurrent.futures
import urllib.request
import urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

HIBP_KEY = os.environ.get("HIBP_KEY", "")

# ==================== АКТУАЛЬНЫЕ ИСТОЧНИКИ ДАННЫХ ====================
SHERLOCK_DATA_URL = "https://raw.githubusercontent.com/sherlock-project/sherlock/refs/heads/master/sherlock_project/resources/data.json"
WMN_DATA_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"

_sherlock_cache = None
_wmn_cache = None

# ==================== ПОЛНАЯ БАЗА DEF-КОДОВ РФ ====================
DEF_DATABASE = {
    # Tele2
    "900": ("Tele2", "Все регионы"),
    "901": ("Скайлинк / МТТ / Сбер-Мобайл", "Все регионы"),
    "902": ("Tele2", "Все регионы"),
    "904": ("Tele2 / МТТ", "Все регионы"),
    "908": ("Tele2 / МегаФон", "Все регионы"),
    "950": ("Tele2", "Все регионы"),
    "951": ("Tele2", "Все регионы"),
    "952": ("Tele2", "Все регионы"),
    "953": ("Tele2", "Все регионы"),
    "977": ("Сбер-Мобайл / Tele2", "Все регионы"),
    "991": ("Ростелеком / Yota", "Все регионы"),
    "994": ("Сбер-Мобайл / Tele2", "Все регионы"),
    # Билайн
    "903": ("Билайн", "Все регионы"),
    "905": ("Билайн", "Все регионы"),
    "906": ("Билайн", "Все регионы"),
    "909": ("Билайн", "Все регионы"),
    "960": ("Билайн", "Все регионы"),
    "961": ("Билайн", "Все регионы"),
    "962": ("Билайн", "Все регионы"),
    "963": ("Билайн", "Все регионы"),
    "964": ("Билайн", "Все регионы"),
    "965": ("Билайн", "Все регионы"),
    "966": ("Билайн / МТТ", "Все регионы"),
    "967": ("Билайн / МТТ", "Все регионы"),
    "968": ("Билайн / МТТ", "Все регионы"),
    "969": ("Билайн / ТВЕ-Телеком", "Все регионы"),
    # МТС
    "910": ("МТС", "Центральный"),
    "911": ("МТС", "Северо-Западный"),
    "912": ("МТС", "Уральский"),
    "913": ("МТС", "Сибирский"),
    "914": ("МТС", "Дальневосточный"),
    "915": ("МТС", "Центральный"),
    "916": ("МТС", "Москва"),
    "917": ("МТС", "Поволжский / Москва"),
    "918": ("МТС", "Южный"),
    "919": ("МТС", "Все регионы"),
    "978": ("МТС / Win Mobile", "Крым"),
    "980": ("МТС / Сбер-Мобайл", "Все регионы"),
    "982": ("МТС / Экспресс-Мобайл", "Все регионы"),
    "983": ("МТС", "Сибирский"),
    "984": ("МТС / ГПБ-Мобайл", "Все регионы"),
    "985": ("МТС / МТТ", "Москва"),
    "986": ("МТС / МТТ", "Все регионы"),
    "987": ("МТС", "Поволжский"),
    "988": ("МТС", "Южный"),
    "989": ("МТС / МТТ", "Южный / Москва"),
    # МегаФон
    "920": ("МегаФон", "Центральный"),
    "921": ("МегаФон", "Северо-Западный"),
    "922": ("МегаФон", "Уральский / Поволжский"),
    "923": ("МегаФон", "Все регионы"),
    "924": ("МегаФон", "Все регионы"),
    "925": ("МегаФон", "Москва"),
    "926": ("МегаФон", "Москва"),
    "927": ("МегаФон", "Поволжский"),
    "928": ("МегаФон", "Южный"),
    "929": ("МегаФон", "Все регионы"),
    "932": ("МегаФон / МТТ", "Все регионы"),
    "934": ("МТТ / МегаФон", "Все регионы"),
    "936": ("МТТ / МегаФон", "Все регионы"),
    "937": ("МегаФон", "Поволжский"),
    "938": ("МегаФон / МТТ", "Все регионы"),
    "939": ("Ростелеком / МегаФон", "Все регионы"),
    "999": ("МегаФон / Yota", "Все регионы"),
    # Yota
    "996": ("Yota", "Все регионы"),
    "997": ("АСВТ / МегаФон", "Москва"),
    "998": ("Yota", "Все регионы"),
    "992": ("Yota / Т-Мобайл", "Все регионы"),
    # Виртуальные (MVNO)
    "930": ("Ростелеком / МТТ", "Все регионы"),
    "931": ("MCN Telecom", "Все регионы"),
    "933": ("Т-Мобайл / ВТБ-Мобайл / Альфа-Мобайл", "Все регионы"),
    "958": ("ТТК / Ростелеком", "Все регионы"),
    "993": ("Т-Мобайл / Сбер-Мобайл", "Все регионы"),
    "995": ("Т-Мобайл", "Все регионы"),
    # Региональные
    "940": ("Мотив", "Екатеринбург"),
    "941": ("Мотив / ЭРА-ГЛОНАСС", "Екатеринбург"),
    "942": ("Мотив / ЭРА-ГЛОНАСС", "Екатеринбург"),
    "943": ("Мотив", "Екатеринбург"),
    "944": ("Мотив", "Екатеринбург"),
    "945": ("Мотив", "Екатеринбург"),
    "946": ("Мотив", "Екатеринбург"),
    "947": ("Мотив", "Екатеринбург"),
    "948": ("Мотив", "Екатеринбург"),
    "949": ("Феникс / Миранда-медиа", "ДНР"),
    "954": ("ГлобалТел (спутник)", "Россия"),
    "955": ("TETRA", "Москва"),
    "956": ("TETRA", "Санкт-Петербург"),
    "959": ("MVNO", "ЛНР"),
    "979": ("Миранда-медиа / Win Mobile", "Крым"),
    "981": ("Экспресс-Мобайл / МТТ", "Все регионы"),
}


def _load_sherlock_data():
    global _sherlock_cache
    if _sherlock_cache is not None:
        return _sherlock_cache
    try:
        req = urllib.request.Request(SHERLOCK_DATA_URL, headers={"User-Agent": "OSINT/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            _sherlock_cache = json.loads(resp.read().decode("utf-8"))
        return _sherlock_cache
    except Exception as e:
        print(f"[sherlock load error] {e}")
        return {}


def _load_wmn_data():
    global _wmn_cache
    if _wmn_cache is not None:
        return _wmn_cache
    try:
        req = urllib.request.Request(WMN_DATA_URL, headers={"User-Agent": "OSINT/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            _wmn_cache = json.loads(resp.read().decode("utf-8"))
        return _wmn_cache
    except Exception as e:
        print(f"[wmn load error] {e}")
        return {}


def _check_site_sherlock(site_name, site_data, username):
    """Проверка по базе Sherlock."""
    try:
        url_template = site_data.get("url", "")
        if not url_template:
            return None
        url = url_template.format(username)
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                status = resp.getcode()
                body = resp.read(3000).decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            status = e.code
            body = ""
        except Exception:
            return None

        error_type = site_data.get("errorType", "status_code")
        if error_type == "status_code":
            if status == 200:
                error_msg = site_data.get("errorMsg", "")
                if error_msg and error_msg in body:
                    return None
                return {"site": site_name, "url": url}
        elif error_type == "message":
            error_msg = site_data.get("errorMsg", "")
            if status == 200:
                if error_msg and error_msg in body:
                    return None
                return {"site": site_name, "url": url}
        return None
    except Exception:
        return None


def _check_site_wmn(site_name, site_data, username):
    """Проверка по базе WhatsMyName."""
    try:
        url_template = site_data.get("uri_check", "")
        if not url_template:
            return None
        url = url_template.format(account=username, username=username)
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                status = resp.getcode()
                body = resp.read(3000).decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            status = e.code
            body = ""
        except Exception:
            return None
        if status == 200:
            error_msg = site_data.get("errorMsg", "")
            if error_msg and error_msg in body:
                return None
            return {"site": site_name, "url": url}
        return None
    except Exception:
        return None


@app.route('/')
def index():
    sherlock = _load_sherlock_data()
    wmn = _load_wmn_data()
    return jsonify({
        "status": "ok",
        "service": "legal-osint",
        "sherlock_sites": len(sherlock),
        "wmn_sites": len(wmn),
        "sherlock_source": SHERLOCK_DATA_URL,
        "wmn_source": WMN_DATA_URL,
        "endpoints": ["/check", "/phone", "/leak"]
    })


@app.route('/check')
def check():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "no username"}), 400

    source = request.args.get('source', 'both').lower()
    found = []
    sites_checked = 0

    if source in ("sherlock", "both"):
        data = _load_sherlock_data()
        if data:
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                futures = {executor.submit(_check_site_sherlock, name, info, username): name
                           for name, info in data.items()}
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        found.append(result)
            sites_checked += len(data)

    if source in ("wmn", "both"):
        data = _load_wmn_data()
        if data:
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                futures = {executor.submit(_check_site_wmn, name, info, username): name
                           for name, info in data.items()}
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        found.append(result)
            sites_checked += len(data)

    # Дедупликация по имени сайта
    seen = set()
    unique = []
    for f in found:
        key = f["site"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(f)

    unique.sort(key=lambda x: x["site"].lower())

    categories = {"Соцсети": [], "Разработка": [], "Игры": [],
                  "Музыка": [], "Фото": [], "Другое": []}
    for f in unique:
        name = f["site"].lower()
        if any(k in name for k in ["git", "code", "dev", "stack", "repl"]):
            categories["Разработка"].append(f["site"])
        elif any(k in name for k in ["steam", "game", "roblox", "chess", "xbox", "psn"]):
            categories["Игры"].append(f["site"])
        elif any(k in name for k in ["sound", "spotify", "music", "last", "bandcamp"]):
            categories["Музыка"].append(f["site"])
        elif any(k in name for k in ["flickr", "photo", "imgur", "deviant", "art"]):
            categories["Фото"].append(f["site"])
        elif any(k in name for k in ["t.me", "vk.com", "reddit", "twitter", "instagram", "facebook", "tiktok"]):
            categories["Соцсети"].append(f["site"])
        else:
            categories["Другое"].append(f["site"])

    return jsonify({
        "username": username,
        "total": len(unique),
        "sites_checked": sites_checked,
        "found": [f["site"] for f in unique],
        "urls": {f["site"]: f["url"] for f in unique},
        "categories": categories
    })


@app.route('/phone')
def phone():
    number = request.args.get('number', '').strip()
    if not number:
        return jsonify({"error": "no number"}), 400

    clean = "".join(c for c in number if c.isdigit())
    operator = "неизвестно"
    region = "неизвестно"
    country = "неизвестно"

    if clean.startswith("7") and len(clean) >= 4:
        code = clean[1:4]
        country = "🇷🇺 Россия/Казахстан"
        if code in DEF_DATABASE:
            operator, region = DEF_DATABASE[code]
        else:
            operator, region = "неизвестный оператор", "Россия"
    elif clean.startswith("380"):
        country = "🇺🇦 Украина"
        operator, region = "Киевстар/Vodafone/Лайфселл", "Украина"
    elif clean.startswith("375"):
        country = "🇧🇾 Беларусь"
        operator, region = "А1/МТС/Беларусь", "Беларусь"
    elif clean.startswith("1"):
        country = "🇺🇸 США/Канада"
        operator, region = "разные операторы", "Северная Америка"
    elif clean.startswith("44"):
        country = "🇬🇧 Великобритания"
        operator, region = "разные операторы", "Европа"
    elif clean.startswith("49"):
        country = "🇩🇪 Германия"
        operator, region = "разные операторы", "Европа"

    return jsonify({
        "number": number,
        "valid": True,
        "country": country,
        "operator": operator,
        "region": region,
        "def_code": clean[1:4] if clean.startswith("7") else None
    })


@app.route('/leak')
def leak():
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({"error": "no email"}), 400
    if not HIBP_KEY:
        return jsonify({"error": "HIBP_KEY not set"}), 500

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"
    headers = {"User-Agent": "OSINT/1.0", "hibp-api-key": HIBP_KEY}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return jsonify({
                "email": email, "total": len(data),
                "breaches": [b.get("Name") for b in data]
            })
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return jsonify({"email": email, "total": 0, "breaches": []})
        return jsonify({"error": f"HIBP error {e.code}"}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
