import datetime
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

def generate_html(results, checked_time, all_healthy):
    items_js = []
    for name, (status_code, is_ok, url) in results.items():
        escaped_name = name.replace('"', '\\"')
        items_js.append('{"name": "' + escaped_name + '", "status": "' + status_code + '", "url": "' + url + '"}')
    items_str = "[" + ", ".join(items_js) + "]"

    favicon_emoji = "🟢" if all_healthy else "🔴"
    favicon_data = "data:image/svg+xml,<svg xmlns='<unsafe_url>http://www.w3.org/2000/svg'</unsafe_url> viewBox='0 0 100 100'><text y='.9em' font-size='90'>" + favicon_emoji + "</text></svg>"

    h = ""
    h += '<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
    h += '<meta charset="UTF-8">\n'
    h += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    h += '<title>Bunsugi Cloud Service Status</title>\n'
    h += '<link rel="icon" href="' + favicon_data + '">\n'
    h += '<meta http-equiv="refresh" content="300">\n'
    h += '<style>\n'
    h += 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }\n'
    h += '.wrapper { max-width: 600px; margin: 20px auto; position: relative; }\n'
    h += '.lang-switcher { display: flex; justify-content: flex-end; margin-bottom: 12px; }\n'
    h += '.pill { display: inline-flex; background: #e0e4e8; border-radius: 50px; padding: 3px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1); }\n'
    h += '.lang-btn { background: transparent; border: none; padding: 6px 16px; border-radius: 50px; cursor: pointer; font-size: 12px; font-weight: 600; color: #666; transition: all 0.2s ease; }\n'
    h += '.lang-btn.active { background: #ffffff; color: #2c3e50; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }\n'
    h += '.container { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }\n'
    h += 'h1 { font-size: 22px; margin-top: 0; margin-bottom: 20px; color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 15px; text-align: center; letter-spacing: 0.5px; }\n'
    h += '.banner { padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 25px; }\n'
    h += '.banner.success { background-color: #e8f8f5; color: #117a65; }\n'
    h += '.banner.danger { background-color: #f8d7da; color: #721c24; }\n'
    h += '.service-list { list-style: none; padding: 0; margin: 0; }\n'
    h += '.service-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #eee; }\n'
    h += '.service-item:last-child { border-bottom: none; }\n'
    h += '.service-name { font-weight: 600; font-size: 16px; }\n'
    h += '.badge-link { text-decoration: none; }\n'
    h += '.badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; transition: opacity 0.2s; }\n'
    h += '.badge:hover { opacity: 0.85; }\n'
    h += '.badge.success { background-color: #2ecc71; color: white; }\n'
    h += '.badge.danger { background-color: #e74c3c; color: white; }\n'
    h += '.footer { margin-top: 25px; font-size: 12px; color: #7f8c8d; text-align: center; }\n'
    h += '</style>\n</head>\n<body>\n'
    h += '<div class="wrapper">\n'
    h += '<div class="lang-switcher"><div class="pill">\n'
    h += '<button class="lang-btn" id="btn-ja" onclick="setLanguage(\'ja\')">日本語</button>\n'
    h += '<button class="lang-btn" id="btn-en" onclick="setLanguage(\'en\')">English</button>\n'
    h += '</div></div>\n'
    h += '<div class="container">\n'
    h += '<h1 id="title"></h1>\n'
    h += '<div id="banner" class="banner"></div>\n'
    h += '<ul class="service-list" id="service-list"></ul>\n'
    h += '<div class="footer">\n'
    h += '<span id="footer-text"></span>: ' + checked_time + ' (JST)<br>\n'
    h += '<span id="footer-note"></span>\n'
    h += '</div></div></div>\n'
    h += '<script>\n'
    h += 'const allHealthy = ' + ("true" if all_healthy else "false") + ';\n'
    h += 'const services = ' + items_str + ';\n'
    h += 'const dict = {\n'
    h += '  ja: { title: "文杉クラウドサービス稼働状況", bannerSuccess: "すべてのサービスは正常に稼働しています", bannerDanger: "一部のサービスに異常・接続エラーを検知しています", statusOk: "正常稼働中", statusError: "接続エラー", footerText: "最終確認日時", footerNote: "※このページは15分おきに自動更新されます" },\n'
    h += '
