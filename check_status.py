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
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid transparent;
  background: #1e293b;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.55;
  transition: all 0.2s ease;
  padding: 0;
}
.flag-btn:hover {
  opacity: 0.9;
  transform: scale(1.06);
}
.flag-btn.active {
  opacity: 1;
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3);
  transform: scale(1.06);
}
.flag-btn svg {
  width: 100%;
  height: 100%;
  display: block;
}
.container {
  background: #1e293b;
  border: 1px solid #334155;
  padding: clamp(20px, 3.2vw, 48px);
  border-radius: clamp(14px, 1.5vw, 24px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}
h1 {
  font-size: clamp(20px, 2.6vw, 44px);
  margin-top: 0;
  margin-bottom: clamp(16px, 2.2vw, 28px);
  color: #f8fafc;
  border-bottom: 1px solid #334155;
  padding-bottom: clamp(12px, 1.5vw, 22px);
  text-align: center;
  letter-spacing: 0.5px;
}
.info-bar {
  display: none;
}
@media (min-width: 900px) {
  .info-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: clamp(12px, 1.6vw, 24px);
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid #334155;
    border-radius: clamp(10px, 1vw, 16px);
    padding: clamp(12px, 1.4vw, 20px) clamp(18px, 2vw, 28px);
    margin-bottom: clamp(18px, 2.2vw, 30px);
  }
}
.datetime-group {
  display: flex;
  align-items: baseline;
  gap: clamp(12px, 1.4vw, 22px);
}
.date-text {
  font-size: clamp(16px, 1.5vw, 26px);
  font-weight: 600;
  color: #cbd5e1;
}
.clock-text {
  font-size: clamp(22px, 2.2vw, 38px);
  font-weight: 700;
  color: #f8fafc;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.03em;
}
.weather-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: clamp(10px, 1.3vw, 20
