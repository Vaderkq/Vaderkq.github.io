import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]
CHANNEL = "vaderkq"

def request(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

# Pobierz token aplikacji Twitch
token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials"
}).encode()

token = request(
    "https://id.twitch.tv/oauth2/token",
    {"Content-Type": "application/x-www-form-urlencoded"},
    token_data
)["access_token"]

headers = {
    "Client-Id": CLIENT_ID,
    "Authorization": f"Bearer {token}"
}

# Znajdź ID kanału
users = request(
    "https://api.twitch.tv/helix/users?login=" + CHANNEL,
    headers
)

if not users.get("data"):
    raise RuntimeError("Nie znaleziono kanału Twitch: " + CHANNEL)

user_id = users["data"][0]["id"]

# Pobierz 5 ostatnich transmisji (archiwów VOD)
videos = request(
    "https://api.twitch.tv/helix/videos?" +
    urllib.parse.urlencode({
        "user_id": user_id,
        "type": "archive",
        "first": 5,
        "sort": "time"
    }),
    headers
)

result = []

for video in videos.get("data", []):
    thumbnail = (
        video["thumbnail_url"]
        .replace("%{width}", "640")
        .replace("%{height}", "360")
    )

    result.append({
        "id": video["id"],
        "title": video["title"],
        "url": video["url"],
        "thumbnail": thumbnail,
        "created_at": video["created_at"],
        "views": video["view_count"],
        "duration": video["duration"]
    })

output = {"channel": CHANNEL, "videos": result}

Path("twitch-vods.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Zapisano {len(result)} transmisji kanału {CHANNEL}.")
