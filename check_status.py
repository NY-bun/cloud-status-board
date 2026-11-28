import datetime
import json
import urllib.request
import urllib.error
import sys

TARGETS = {
    "Outlook / Microsoft 365": "https://status.office365.com/",
    "BLEND": "https://status.motivationworks.co.jp/",
    "ロイロノート": "https://status.loilonote.app/ja",
    "Canva": "https://www.canvastatus.com/",
    "Zoom": "https://www.zoomstatus.com/",
    "L-Gate": "https://l-gate-status.info/"
}

# 杉並区付近の緯度・経度（必要に応じて変更可能）
LATITUDE = 35.6995
LONGITUDE = 139.6364

WMO_WEATHER_LABELS = {
    0: ("快晴", "Clear sky", "☀️"),
    1: ("晴れ", "Mainly clear", "🌤️"),
    2: ("一部くもり", "Partly cloudy", "⛅"),
    3: ("くもり", "Overcast", "☁️"),
    45: ("霧", "Fog", "🌫️"),
    48: ("霧氷", "Depositing rime fog", "🌫️"),
    51: ("弱い霧雨", "Light drizzle", "🌦️"),
    53: ("霧雨", "Moderate drizzle", "🌦️"),
    55: ("強い霧雨", "Dense drizzle", "🌦️"),
    61: ("弱い雨", "Slight rain", "🌧️"),
    63: ("雨", "Moderate rain", "🌧️"),
    65: ("強い雨", "Heavy rain", "🌧️"),
    71: ("弱い雪", "Slight snow", "🌨️"),
    73: ("雪", "Moderate snow", "❄️"),
    75: ("強い雪", "Heavy snow", "❄️"),
    80: ("にわか雨", "Rain showers", "🌦️"),
    81: ("強いにわか雨", "Moderate showers", "🌧️"),
    82: ("激しいにわか雨", "Violent showers", "⛈️"),
    95: ("雷雨", "Thunderstorm", "⛈️"),
}

JP_FLAG_SVG = (
    '<svg viewBox="0 0 36 36" width="100%" height="100%" aria-hidden="true">'
    '<rect width="36" height="36" fill="#ffffff"/>'
    '<circle cx="18" cy="18" r="7.5" fill="#bc002d"/>'
    '</svg>'
)

US_FLAG_SVG = (
    '<svg viewBox="0 0 36 36" width="100%" height="100%" aria-hidden="true">'
    '<rect width="36" height="36" fill="#ffffff"/>'
    '<rect y="0" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="5.5" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="11.1" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="16.6" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="22.2" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="27.7" width="36" height="2.8" fill="#b22234"/>'
    '<rect y="33.2" width="36" height="2.8" fill="#b22234"/>'
    '<rect x="0" y="0" width="18" height="19.4" fill="#3c3b6e"/>'
    '</svg>'
)

def check_service(url):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return "ok", True
            else:
                return "error", False
    except Exception as e:
        print(f"Warning: Failed to check {url} - {e}")
        return "error", False

def fetch_weather(lat=LATITUDE, lon=LONGITUDE):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,weather_code"
        f"&hourly=precipitation_probability"
        f"&timezone=Asia%2FTokyo&forecast_days=1"
    )
    fallback = {
        "available": False,
        "icon": "🌡️",
        "ja": "取得不可",
        "en": "N/A",
        "temp": "--",
        "precip": "--"
    }
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data.get("current", {})
        code = current.get("weather_code")
        temp_val = current.get("temperature_2m")
        temp_str = f"{round(temp_val, 1)}°C" if isinstance(temp_val, (int, float)) else "--"

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        probs = hourly.get("precipitation_probability", [])
        cur_time_str = current.get("time", "")
        cur_hour_prefix = cur_time_str[:13] if len(cur_time_str) >= 13 else ""

        precip_str = "--"
        if cur_hour_prefix and len(times) == len(probs):
            for t_str, p_val in zip(times, probs):
                if t_str.startswith(cur_hour_prefix) and p_val is not None:
                    precip_str = f"{p_val}%"
                    break
        if precip_str == "--" and probs:
            first_prob = next((p for p in probs if p is not None), None)
            if first_prob is not None:
                precip_str = f"{first_prob}%"

        ja_label, en_label, icon = WMO_WEATHER_LABELS.get(
            code, ("その他", "Other", "🌡️")
        )
        return {
            "available": True,
            "icon": icon,
            "ja": ja_label,
            "en": en_label,
            "temp": temp_str,
            "precip": precip_str
        }
    except Exception as e:
        print(f"Warning: Failed to fetch weather - {e}")
        return fallback

def generate_html(results, checked_time, all_healthy, weather):
    items_js = []
    for name, (status_code, is_ok, url) in results.items():
        escaped_name = name.replace('"', '\\"')
        items_js.append('{"name": "' + escaped_name + '", "status": "' + status_code + '", "url": "' + url + '"}')
    items_str = "[" + ", ".join(items_js) + "]"
    weather_json = json.dumps(weather, ensure_ascii=False)

    favicon_emoji = "🟢" if all_healthy else "🔴"
    favicon_data = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>" + favicon_emoji + "</text></svg>"

    h = ""
    h += '<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
    h += '<meta charset="UTF-8">\n'
    h += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    h += '<title>Bunsugi Cloud Service Status</title>\n'
    h += '<link rel="icon" href="' + favicon_data + '">\n'
    h += '<meta http-equiv="refresh" content="300">\n'
    h += '<style>\n'
    h += '* { box-sizing: border-box; }\n'
    h += 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: clamp(12px, 2.5vw, 32px); padding-bottom: clamp(88px, 8vw, 124px); min-height: 100vh; display: flex; flex-direction: column; justify-content: center; }\n'
    h += '.wrapper { width: 100%; max-width: 1440px; margin: 0 auto; }\n'
    h += '.lang-fab { position: fixed; right: clamp(16px, 2.2vw, 32px); bottom: clamp(16px, 2.2vw, 32px); z-index: 100; display: inline-flex; align-items: center; gap: clamp(8px, 0.8vw, 12px); background: rgba(30, 41, 59, 0.94); backdrop-filter: blur(8px); border: 1px solid #334155; border-radius: 999px; padding: clamp(6px, 0.6vw, 10px); box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); }\n'
    h += '.flag-btn { width: clamp(40px, 3.6vw, 56px); height: clamp(40px, 3.6vw, 56px); border-radius: 50%; overflow: hidden; border: 2px solid transparent; background: #1e293b; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; opacity: 0.55; transition: all 0.2s ease; padding: 0; }\n'
    h += '.flag-btn:hover { opacity: 0.9; transform: scale(1.06); }\n'
    h += '.flag-btn.active { opacity: 1; border-color: #38bdf8; box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3); transform: scale(1.06); }\n'
    h += '.flag-btn svg { width: 100%; height: 100%; display: block; }\n'
    h += '.container { background: #1e293b; border: 1px solid #334155; padding: clamp(20px, 3.2vw, 48px); border-radius: clamp(14px, 1.5vw, 24px); box-shadow: 0 12px 32px rgba(0,0,0,0.4); }\n'
    h += 'h1 { font-size: clamp(20px, 2.6vw, 44px); margin-top: 0; margin-bottom: clamp(16px, 2.2vw, 28px); color: #f8fafc; border-bottom: 1px solid #334155; padding-bottom: clamp(12px, 1.5vw, 22px); text-align: center; letter-spacing: 0.5px; }\n'
    h += '.info-bar { display: none; }\n'
    h += '@media (min-width: 900px) { .info-bar { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: clamp(12px, 1.6vw, 24px); background: rgba(15, 23, 42, 0.7); border: 1px solid #334155; border-radius: clamp(10px, 1vw, 16px); padding: clamp(12px, 1.4vw, 20px) clamp(18px, 2vw, 28px); margin-bottom: clamp(18px, 2.2vw, 30px); } }\n'
    h += '.datetime-group { display: flex; align-items: baseline; gap: clamp(12px, 1.4vw, 22px); }\n'
    h += '.date-text { font-size: clamp(16px, 1.5vw, 26px); font-weight: 600; color: #cbd5e1; }\n'
    h += '.clock-text { font-size: clamp(22px, 2.2vw, 38px); font-weight: 700; color: #f8fafc; font-variant-numeric: tabular-nums; letter-spacing: 0.03em; }\n'
    h += '.weather-group { display: flex; flex-wrap: wrap;
