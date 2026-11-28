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
    favicon_data = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>" + favicon_emoji + "</text></svg>"

    h = ""
    h += '<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
    h += '<meta charset="UTF-8">\n'
    h += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    h += '<title>Bunsugi Cloud Service Status</title>\n'
    h += '<link rel="icon" href="' + favicon_data + '">\n'
    h += '<meta http-equiv="refresh" content="300">\n'
    h += '<style>\n'
    h += 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }\n'
    h += '.wrapper { max-width: 600px; margin: 20px auto; position: relative; }\n'
    h += '.lang-switcher { display: flex; justify-content: flex-end; margin-bottom: 12px; }\n'
    h += '.pill { display: inline-flex; background: #1e293b; border: 1px solid #334155; border-radius: 50px; padding: 3px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.4); }\n'
    h += '.lang-btn { background: transparent; border: none; padding: 6px 16px; border-radius: 50px; cursor: pointer; font-size: 12px; font-weight: 600; color: #94a3b8; transition: all 0.2s ease; }\n'
    h += '.lang-btn:hover { color: #f8fafc; }\n'
    h += '.lang-btn.active { background: #334155; color: #f8fafc; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }\n'
    h += '.container { background: #1e293b; border: 1px solid #334155; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.35); }\n'
    h += 'h1 { font-size: 22px; margin-top: 0; margin-bottom: 20px; color: #f8fafc; border-bottom: 1px solid #334155; padding-bottom: 15px; text-align: center; letter-spacing: 0.5px; }\n'
    h += '.banner { padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 25px; border: 1px solid transparent; }\n'
    h += '.banner.success { background-color: rgba(16, 185, 129, 0.14); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.35); }\n'
    h += '.banner.danger { background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; border-color: rgba(239, 68, 68, 0.35); }\n'
    h += '.service-list { list-style: none; padding: 0; margin: 0; }\n'
    h += '.service-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #334155; }\n'
    h += '.service-item:last-child { border-bottom: none; }\n'
    h += '.service-name { font-weight: 600; font-size: 16px; color: #f1f5f9; }\n'
    h += '.badge-link { text-decoration: none; }\n'
    h += '.badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; transition: opacity 0.2s, transform 0.15s; }\n'
    h += '.badge:hover { opacity: 0.9; transform: translateY(-1px); }\n'
    h += '.badge.success { background-color: #10b981; color: #052e16; }\n'
    h += '.badge.danger { background-color: #ef4444; color: #ffffff; }\n'
    h += '.footer { margin-top: 25px; font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.6; }\n'
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
    h += '  ja: { title: "文杉クラウドサービス稼働状況", bannerSuccess: "すべてのサービスは正常に稼働しています", bannerDanger: "一部のサービスに異常・接続エラーを検知しています", statusOk: "正常稼働中", statusError: "接続エラー", footerText: "最終確認日時", footerNote: "※このページは10分おきに自動更新されます" },\n'
    h += '  en: { title: "Bunsugi Cloud Service Status", bannerSuccess: "All services are operating normally", bannerDanger: "Issues or connection errors detected", statusOk: "Operational", statusError: "Connection Error", footerText: "Last checked", footerNote: "*This page automatically refreshes every 10 minutes" }\n'
    h += '};\n'
    h += 'function setLanguage(lang) {\n'
    h += '  document.getElementById("btn-ja").classList.toggle("active", lang === "ja");\n'
    h += '  document.getElementById("btn-en").classList.toggle("active", lang === "en");\n'
    h += '  const t = dict[lang] || dict.en;\n'
    h += '  document.getElementById("title").innerText = t.title;\n'
    h += '  const banner = document.getElementById("banner");\n'
    h += '  banner.className = "banner " + (allHealthy ? "success" : "danger");\n'
    h += '  banner.innerText = allHealthy ? t.bannerSuccess : t.bannerDanger;\n'
    h += '  document.getElementById("footer-text").innerText = t.footerText;\n'
    h += '  document.getElementById("footer-note").innerText = t.footerNote;\n'
    h += '  const list = document.getElementById("service-list");\n'
    h += '  list.innerHTML = "";\n'
    h += '  services.forEach(s => {\n'
    h += '    const isOk = s.status === "ok";\n'
    h += '    const badgeClass = isOk ? "success" : "danger";\n'
    h += '    const statusText = isOk ? t.statusOk : t.statusError;\n'
    h += '    let displayName = s.name;\n'
    h += '    if (lang === "en" && displayName === "ロイロノート") { displayName = "LoiLoNote"; }\n'
    h += '    const li = document.createElement("li");\n'
    h += '    li.className = "service-item";\n'
    h += '    li.innerHTML = \'<span class="service-name">\' + displayName + \'</span><a href="\' + s.url + \'" target="_blank" rel="noopener noreferrer" class="badge-link"><span class="badge \' + badgeClass + \'">\' + statusText + \'</span></a>\';\n'
    h += '    list.appendChild(li);\n'
    h += '  });\n'
    h += '}\n'
    h += 'const userLang = navigator.language || navigator.userLanguage;\n'
    h += 'const initialLang = userLang.startsWith("ja") ? "ja" : "en";\n'
    h += 'setLanguage(initialLang);\n'
    h += '</script>\n</body>\n</html>\n'

    return h

def main():
    try:
        results = {}
        all_healthy = True

        for name, url in TARGETS.items():
            status_code, is_ok = check_service(url)
            results[name] = (status_code, is_ok, url)
            if not is_ok:
                all_healthy = False

        jst = datetime.timezone(datetime.timedelta(hours=9))
        checked_time = datetime.datetime.now(jst).strftime('%Y-%m-%d %H:%M:%S')

        html_output = generate_html(results, checked_time, all_healthy)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        print("index.html generated successfully.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
