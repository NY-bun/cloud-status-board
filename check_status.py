import datetime
import urllib.request
import urllib.error

TARGETS = {
    "Outlook / Microsoft 365": "https://status.office365.com/",
    "BLEND": "https://status.motivationworks.co.jp/",
    "ロイロノート": "https://status.loilonote.app/ja"
}

def check_service(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "ok", True
            else:
                return "error", False
    except Exception as e:
        return "error", False

def generate_html(results, checked_time, all_healthy):
    # JSON風のデータ構造をHTML内に埋め込む
    items_js = []
    for name, (status_code, is_ok, url) in results.items():
        items_js.append(f'{{name: "{name}", status: "{status_code}", url: "{url}"}}')
    items_str = "[" + ", ".join(items_js) + "]"

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Service Status</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f4f7f6;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            position: relative;
        }}
        .lang-switcher {{
            position: absolute;
            top: 20px;
            right: 30px;
            display: flex;
            gap: 5px;
        }}
        .lang-btn {{
            background: #eee;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            color: #555;
        }}
        .lang-btn.active {{
            background: #3498db;
            color: white;
        }}
        h1 {{
            font-size: 20px;
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 12px;
            padding-right: 100px;
        }}
        .banner {{
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 25px;
        }}
        .banner.success {{ background-color: #e8f8f5; color: #117a65; }}
        .banner.danger {{ background-color: #f8d7da; color: #721c24; }}
        .service-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .service-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }}
        .service-item:last-child {{ border-bottom: none; }}
        .service-name {{ font-weight: 600; font-size: 16px; }}
        .badge-link {{
            text-decoration: none;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            transition: opacity 0.2s;
        }}
        .badge:hover {{
            opacity: 0.85;
        }}
        .badge.success {{ background-color: #2ecc71; color: white; }}
        .badge.danger {{ background-color: #e74c3c; color: white; }}
        .footer {{
            margin-top: 25px;
            font-size: 12px;
            color: #7f8c8d;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="lang-switcher">
            <button class="lang-btn" id="btn-ja" onclick="setLanguage('ja')">日本語</button>
            <button class="lang-btn" id="btn-en" onclick="setLanguage('en')">English</button>
        </div>
        
        <h1 id="title"></h1>
        <div id="banner" class="banner"></div>
        
        <ul class="service-list" id="service-list"></ul>
        
        <div class="footer">
            <span id="footer-text"></span>: {checked_time} (JST)<br>
            <span id="footer-note"></span>
        </div>
    </div>

    <script>
        const allHealthy = {"true" if all_healthy else "false"};
        const services = {items_str};

        const dict = {{
            ja: {{
                title: "🛠️ クラウドサービス ステータス",
                bannerSuccess: "すべてのサービスは正常に稼働しています",
                bannerDanger: "一部のサービスに異常・接続エラーを検知しています",
                statusOk: "正常稼働中",
                statusError: "接続エラー",
                footerText: "最終確認日時",
                footerNote: "※このページは15分おきに自動更新されます"
            }},
            en: {{
                title: "🛠️ Cloud Service Status",
                bannerSuccess: "All services are operating normally",
                bannerDanger: "Issues or connection errors detected",
                statusOk: "Operational",
                statusError: "Connection Error",
                footerText: "Last checked",
                footerNote: "*This page automatically refreshes every 15 minutes"
            }}
        }};

        function setLanguage(lang) {{
            // ボタンのアクティブ状態更新
            document.getElementById('btn-ja').classList.toggle('active', lang === 'ja');
            document.getElementById('btn-en').classList.toggle('active', lang === 'en');

            const t = dict[lang] || dict.en;

            // テキストの適用
            document.getElementById('title').innerText = t.title;
            
            const banner = document.getElementById('banner');
            banner.className = "banner " + (allHealthy ? "success" : "danger");
            banner.innerText = allHealthy ? t.bannerSuccess : t.bannerDanger;

            document.getElementById('footer-text').innerText = t.footerText;
            document.getElementById('footer-note').innerText = t.footerNote;

            // リストの生成
            const list = document.getElementById('service-list');
            list.innerHTML = '';
            
            services.forEach(s => {{
                const isOk = s.status === 'ok';
                const badgeClass = isOk ? 'success' : 'danger';
                const statusText = isOk ? t.statusOk : t.statusError;

                const li = document.createElement('li');
                li.className = 'service-item';
                li.innerHTML = `
                    <span class="service-name">${{s.name}}</span>
                    <a href="${{s.url}}" target="_blank" rel="noopener noreferrer" class="badge-link">
                        <span class="badge ${{badgeClass}}">${{statusText}}</span>
                    </a>
                `;
                list.appendChild(li);
            }});
        }}

        // 初期化: ブラウザ言語判定 (jaが含まれれば日本語、それ以外は英語)
        const userLang = navigator.language || navigator.userLanguage;
        const initialLang = userLang.startsWith('ja') ? 'ja' : 'en';
        setLanguage(initialLang);
    </script>
</body>
</html>
"""
    return html_content

def main():
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

if __name__ == "__main__":
    main()
