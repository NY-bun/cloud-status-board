import os
import datetime
import urllib.request
import urllib.error
import pytz

# チェック対象のサービス定義
TARGETS = {
    "Outlook / Microsoft 365": "https://status.office365.com/",
    "BLEND": "https://status.motivationworks.co.jp/", # 各自治体・学校等のURLに合わせて変更
    "ロイロノート": "https://status.loilonote.app/ja"
}

def check_service(url):
    """Webサイトの応答（HTTP 200）をチェック"""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return "正常稼働中", "success", True
            else:
                return f"異常応答 (HTTP {response.status})", "danger", False
    except Exception as e:
        return f"接続エラー", "danger", False

def generate_html(results, checked_time, all_healthy):
    """スマホやPCで見やすいHTMLを生成"""
    status_banner_class = "success" if all_healthy else "danger"
    status_banner_text = "すべてのサービスは正常に稼働しています" if all_healthy else "一部のサービスに異常・接続エラーを検知しています"

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>社内クラウドサービス 稼働ステータス</title>
    <meta http-equiv="refresh" content="300"> <!-- 5分ごとに自動リロード -->
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
        }}
        h1 {{
            font-size: 20px;
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 12px;
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
        .badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
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
        <h1>🛠️ クラウドサービス ステータス</h1>
        <div class="banner {status_banner_class}">
            {status_banner_text}
        </div>
        <ul class="service-list">
"""

    for name, (status_text, badge_class, _) in results.items():
        html_content += f"""
            <li class="service-item">
                <span class="service-name">{name}</span>
                <span class="badge {badge_class}">{status_text}</span>
            </li>
"""

    html_content += f"""
        </ul>
        <div class="footer">
            最終確認日時: {checked_time} (JST)<br>
            ※このページは毎朝5:00に自動更新されます
        </div>
    </div>
</body>
</html>
"""
    return html_content

def main():
    results = {}
    all_healthy = True

    for name, url in TARGETS.items():
        status_text, badge_class, is_ok = check_service(url)
        results[name] = (status_text, badge_class, is_ok)
        if not is_ok:
            all_healthy = False

    # 日本時間の現在時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    checked_time = datetime.datetime.now(jst).strftime('%Y-%m-%d %H:%M:%S')

    # index.htmlを出力
    html_output = generate_html(results, checked_time, all_healthy)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("index.html generated successfully.")

if __name__ == "__main__":
    main()
