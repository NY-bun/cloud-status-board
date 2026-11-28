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
   :root{
    --bg:#0f172a;
    --card:#1e293b;
    --text:#f8fafc;
    --sub:#cbd5e1;
    --border:#334155;
    --ok:#22c55e;
    --ok-bg:#14532d;
    --error:#ef4444;
    --error-bg:#7f1d1d;
}

*{
    box-sizing:border-box;
}

html{
    font-size:16px;
}

body{
    margin:0;
    padding:16px;
    font-family:-apple-system,BlinkMacSystemFont,
                "Segoe UI",Roboto,
                "Helvetica Neue",Arial,sans-serif;

    background:var(--bg);
    color:var(--text);

    min-height:100vh;
}

.wrapper{
    width:100%;
    max-width:1400px;
    margin:0 auto;
}

.lang-switcher{
    display:flex;
    justify-content:flex-end;
    margin-bottom:12px;
}

.pill{
    display:inline-flex;
    background:#334155;
    border-radius:50px;
    padding:3px;
}

.lang-btn{
    background:transparent;
    border:none;
    color:#cbd5e1;
    cursor:pointer;
    padding:8px 16px;
    border-radius:50px;
    font-size:14px;
}

.lang-btn.active{
    background:#475569;
    color:white;
}

.container{
    background:var(--card);
    border-radius:20px;
    padding:clamp(16px, 3vw, 40px);

    box-shadow:
        0 10px 30px rgba(0,0,0,.35);
}

h1{
    text-align:center;

    font-size:
        clamp(24px, 4vw, 54px);

    margin:0;
    padding-bottom:20px;

    border-bottom:
        2px solid var(--border);

    color:white;
}

.header-panel{
    text-align:center;

    padding:20px 0;
}

#datetime{
    font-size:
        clamp(20px, 3vw, 42px);

    font-weight:700;
    margin-bottom:12px;
}

#weather{
    font-size:
        clamp(18px, 2.5vw, 32px);

    color:var(--sub);
}

.banner{
    text-align:center;

    border-radius:12px;

    padding:
      clamp(12px,2vw,24px);

    margin-bottom:24px;

    font-weight:700;

    font-size:
        clamp(15px, 2vw, 28px);
}

.banner.success{
    background:var(--ok-bg);
    color:#bbf7d0;
}

.banner.danger{
    background:var(--error-bg);
    color:#fecaca;
}

.service-list{
    list-style:none;
    padding:0;
    margin:0;
}

.service-item{
    display:flex;
    justify-content:space-between;
    align-items:center;

    gap:16px;

    padding:18px 0;

    border-bottom:
        1px solid var(--border);
}

.service-item:last-child{
    border-bottom:none;
}

.service-name{
    font-size:
        clamp(16px, 2vw, 30px);

    font-weight:600;
}

.badge-link{
    text-decoration:none;
}

.badge{
    display:inline-block;

    padding:
      clamp(8px,1vw,12px)
      clamp(16px,2vw,28px);

    border-radius:999px;

    font-size:
      clamp(13px,1.7vw,22px);

    font-weight:700;

    white-space:nowrap;
}

.badge.success{
    background:var(--ok);
    color:white;
}

.badge.danger{
    background:var(--error);
    color:white;
}

.footer{
    margin-top:24px;

    text-align:center;

    color:#94a3b8;

    font-size:
      clamp(12px,1.2vw,18px);

    line-height:1.8;
}

/* スマホ */

@media (max-width:768px){

    body{
        padding:10px;
    }

    .lang-switcher{
        justify-content:center;
    }

    .service-item{
        flex-direction:column;
        align-items:flex-start;
    }

    .badge{
        align-self:flex-end;
    }

    .container{
        padding:18px;
    }
}

/* 大型モニター */

@media (min-width:1600px){

    .container{
        padding:50px;
    }

    .service-item{
        padding:24px 0;
    }
}
    h += '<div class="wrapper">\n'
    h += '<div class="lang-switcher"><div class="pill">\n'
    h += '<button class="lang-btn" id="btn-ja" onclick="setLanguage(\'ja\')">日本語</button>\n'
    h += '<button class="lang-btn" id="btn-en" onclick="setLanguage(\'en\')">English</button>\n'
    h += '</div></div>\n'
    h += '<div class="container">\n'
    h += '<h1 id="title"></h1>\n'
<div class="header-panel">
    <div id="datetime"></div>
    <div id="weather"></div>
</div>
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
