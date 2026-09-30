import os
import json
import concurrent.futures
import urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)

# 100 самых популярных сайтов (без Maigret)
SITES = [
    ("GitHub", "https://github.com/{u}"),
    ("Telegram", "https://t.me/{u}"),
    ("Reddit", "https://reddit.com/user/{u}"),
    ("VK", "https://vk.com/{u}"),
    ("Twitter/X", "https://x.com/{u}"),
    ("Instagram", "https://instagram.com/{u}"),
    ("TikTok", "https://tiktok.com/@{u}"),
    ("YouTube", "https://youtube.com/@{u}"),
    ("Twitch", "https://twitch.tv/{u}"),
    ("Steam", "https://steamcommunity.com/id/{u}"),
    ("SoundCloud", "https://soundcloud.com/{u}"),
    ("Spotify", "https://open.spotify.com/user/{u}"),
    ("Pinterest", "https://pinterest.com/{u}"),
    ("Flickr", "https://flickr.com/people/{u}"),
    ("Behance", "https://behance.net/{u}"),
    ("Dribbble", "https://dribbble.com/{u}"),
    ("Medium", "https://medium.com/@{u}"),
    ("Tumblr", "https://{u}.tumblr.com"),
    ("WordPress", "https://{u}.wordpress.com"),
    ("About.me", "https://about.me/{u}"),
    ("Patreon", "https://patreon.com/{u}"),
    ("Keybase", "https://keybase.io/{u}"),
    ("Mastodon", "https://mastodon.social/@{u}"),
    ("Letterboxd", "https://letterboxd.com/{u}"),
    ("Strava", "https://strava.com/athletes/{u}"),
    ("Goodreads", "https://goodreads.com/{u}"),
    ("Wattpad", "https://wattpad.com/user/{u}"),
    ("Duolingo", "https://duolingo.com/profile/{u}"),
    ("MyAnimeList", "https://myanimelist.net/profile/{u}"),
    ("AniList", "https://anilist.co/user/{u}"),
    ("Trakt", "https://trakt.tv/users/{u}"),
    ("Untappd", "https://untappd.com/user/{u}"),
    ("Gravatar", "https://gravatar.com/{u}"),
    ("Disqus", "https://disqus.com/by/{u}"),
    ("SlideShare", "https://slideshare.net/{u}"),
    ("Scribd", "https://scribd.com/{u}"),
    ("Issuu", "https://issuu.com/{u}"),
    ("OK.ru", "https://ok.ru/{u}"),
    ("Habr", "https://habr.com/ru/users/{u}"),
    ("Pikabu", "https://pikabu.ru/@{u}"),
    ("Rutube", "https://rutube.ru/channel/{u}"),
    ("LiveJournal", "https://{u}.livejournal.com"),
    ("Drive2", "https://drive2.ru/users/{u}"),
    ("Sports.ru", "https://sports.ru/profile/{u}"),
    ("Discord", "https://discord.com/users/{u}"),
    ("Skype", "https://join.skype.com/invite/{u}"),
    ("AngelList", "https://angel.co/u/{u}"),
    ("Crunchbase", "https://crunchbase.com/person/{u}"),
    ("ProductHunt", "https://producthunt.com/@{u}"),
    ("Linktree", "https://linktr.ee/{u}"),
    ("Beacons", "https://beacons.ai/{u}"),
    ("Ko-fi", "https://ko-fi.com/{u}"),
    ("BuyMeACoffee", "https://buymeacoffee.com/{u}"),
    ("Etsy", "https://etsy.com/shop/{u}"),
    ("eBay", "https://ebay.com/usr/{u}"),
    ("GitLab", "https://gitlab.com/{u}"),
    ("Bitbucket", "https://bitbucket.org/{u}"),
    ("Replit", "https://replit.com/@{u}"),
    ("Codeberg", "https://codeberg.org/{u}"),
    ("HackerNews", "https://news.ycombinator.com/user?id={u}"),
    ("Dev.to", "https://dev.to/{u}"),
    ("StackOverflow", "https://stackoverflow.com/users/{u}"),
    ("Codepen", "https://codepen.io/{u}"),
    ("Kaggle", "https://kaggle.com/{u}"),
    ("DockerHub", "https://hub.docker.com/u/{u}"),
    ("NPM", "https://npmjs.com/~{u}"),
    ("PyPI", "https://pypi.org/user/{u}"),
    ("Vimeo", "https://vimeo.com/{u}"),
    ("Dailymotion", "https://dailymotion.com/{u}"),
    ("Kick", "https://kick.com/{u}"),
    ("Rumble", "https://rumble.com/user/{u}"),
    ("Odysee", "https://odysee.com/@{u}"),
    ("Last.fm", "https://last.fm/user/{u}"),
    ("Bandcamp", "https://{u}.bandcamp.com"),
    ("Mixcloud", "https://mixcloud.com/{u}"),
    ("Chess.com", "https://chess.com/member/{u}"),
    ("Lichess", "https://lichess.org/@/{u}"),
    ("NameMC", "https://namemc.com/profile/{u}"),
    ("Faceit", "https://faceit.com/en/players/{u}"),
    ("Osu!", "https://osu.ppy.sh/users/{u}"),
    ("Speedrun", "https://speedrun.com/user/{u}"),
    ("DeviantArt", "https://deviantart.com/{u}"),
    ("ArtStation", "https://artstation.com/{u}"),
    ("500px", "https://500px.com/p/{u}"),
    ("Imgur", "https://imgur.com/user/{u}"),
    ("VSCO", "https://vsco.co/{u}"),
    ("Substack", "https://{u}.substack.com"),
    ("Blogger", "https://{u}.blogspot.com"),
    ("Ghost", "https://{u}.ghost.io"),
    ("Write.as", "https://write.as/{u}"),
    ("Telegra.ph", "https://telegra.ph/{u}"),
    ("Notion", "https://notion.so/{u}"),
    ("Carrd", "https://{u}.carrd.co"),
    ("Wattpad", "https://wattpad.com/user/{u}"),
    ("ArchiveOfOurOwn", "https://archiveofourown.org/users/{u}"),
    ("Vivino", "https://vivino.com/users/{u}"),
    ("AllTrails", "https://alltrails.com/members/{u}"),
    ("Ravelry", "https://ravelry.com/people/{u}"),
    ("Couchsurfing", "https://couchsurfing.com/people/{u}"),
]


def _check_site(site_name, template, username):
    """Проверяет один сайт. Возвращает (название, url) или None."""
    try:
        url = template.format(u=username, username=username, account=username)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.getcode() == 200:
                return (site_name, url)
    except Exception:
        pass
    return None


@app.route('/check')
def check():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "no username"}), 400

    found = []
    try:
        # Параллельная проверка — все сайты одновременно
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(_check_site, name, tpl, username)
                for name, tpl in SITES
            ]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    found.append(result)

        return jsonify({
            "username": username,
            "total": len(found),
            "found": [name for name, url in found],
            "urls": {name: url for name, url in found}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return jsonify({"status": "ok", "service": "osint-checker", "sites": len(SITES)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
