import datetime
import json
import subprocess
import urllib.request
import sys

TARGETS = {
    "Outlook / Microsoft 365": "https://status.office365.com/",
    "BLEND": "https://status.motivationworks.co.jp/",
    "ロイロノート": "https://status.loilonote.app/ja",
    "Canva": "https://www.canvastatus.com/",
    "Zoom": "https://www.zoomstatus.com/",
    "L-Gate": "https://l-gate-status.info/"
}

# 監視する共有フォルダ設定（複数追加可能）
SHARE_TARGETS = [
    {
        "name": "共有フォルダ (bunka-srv1\\test)",
        "name_en": "Shared Folder (bunka-srv1\\test)",
        "server": "bunka-srv1",
        "share": r"\\bunka-srv1\test",
        "url": r"\\bunka-srv1\test",
    }
]

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

JP_FLAG_SVG = """<svg viewBox="0 0 36 36" width="100%" height="100%" aria-hidden="true">
  <rect width="36" height="36" fill="#ffffff"/>
  <circle cx="18" cy="18" r="7.5" fill="#bc002d"/>
</svg>"""

US_FLAG_SVG = """<svg viewBox="0 0 36 36" width="100%" height="100%" aria-hidden="true">
  <rect width="36" height="36" fill="#ffffff"/>
  <rect y="0" width="36" height="2.8" fill="#b22234"/>
  <rect y="5.5" width="36" height="2.8" fill="#b22234"/>
  <rect y="11.1" width="36" height="2.8" fill="#b22234"/>
  <rect y="16.6" width="36" height="2.8" fill="#b22234"/>
  <rect y="22.2" width="36" height="2.8" fill="#b22234"/>
  <rect y="27.7" width="36" height="2.8" fill="#b22234"/>
  <rect y="33.2" width="36" height="2.8" fill="#b22234"/>
  <rect x="0" y="0" width="18" height="19.4" fill="#3c3b6e"/>
</svg>"""

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bunsugi Cloud Service Status</title>
<link rel="icon" href="__FAVICON_DATA__">
<meta http-equiv="refresh" content="300">
"""

CSS_TEMPLATE = """<style>
* {
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #0f172a;
  color: #e2e8f0;
  margin: 0;
  padding: clamp(12px, 2.5vw, 32px);
  padding-bottom: clamp(88px, 8vw, 124px);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.wrapper {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
}
.lang-fab {
  position: fixed;
  right: clamp(16px, 2.2vw, 32px);
  bottom: clamp(16px, 2.2vw, 32px);
  z-index: 100;
  display: inline-flex;
  align-items: center;
  gap: clamp(8px, 0.8vw, 12px);
  background: rgba(30, 41, 59, 0.94);
  backdrop-filter: blur(8px);
  border: 1px solid #334155;
  border-radius: 999px;
  padding: clamp(6px, 0.6vw, 10px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
}
.flag-btn {
  width: clamp(40px, 3.6vw, 56px);
  height: clamp(40px, 3.6vw, 56px);
  border-radius: 5