import datetime
import urllib.request
import urllib.error
import sys

TARGETS = {
    "Outlook / Microsoft 365": "https://status.office365.com/",
    "BLEND": "https://status.motivationworks.co.jp/",
    "ロイロノート": "https://status.loilonote.app/ja",
    "Zoom": "https://www.zoomstatus.com/",
    "L-Gate": "https://l-gate-status.info/",
    "Canva": "https://www.canvastatus.com/"
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
        items_js.append(f'{{name: "{name}", status: "{status_code}", url: "{url}"}}')
    items_str = "[" + ", ".join(items_js) + "]"

    favicon_emoji = "🟢" if all_healthy else "🔴"
    favicon_data = f"data:image/svg+xml,<svg xmlns='<unsafe_url>http://www.w3.org/2000/svg'</unsafe_url> viewBox='0 0 100 100'><text y='.9em' font-size='90'>{favicon_emoji}</text></svg>"

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bunsugi Cloud Service Status</title>
    <link rel="icon" href="{favicon_data}">
    <meta http-equiv="refresh" content="300">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f4f7f6;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .wrapper {{
            max-width: 600px;
            margin: 20px auto;
            position: relative;
        }}
        .lang-switcher {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 12px;
        }}
        .pill {{
            display: inline-flex;
            background: #e0e4e8;
            border-radius: 50px;
            padding: 3px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }}
        .lang-btn {{
            background: transparent;
            border: none;
            padding: 6px 16px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            color: #666;
            transition: all 0.2s ease;
        }}
        .lang-btn.active {{
            background: #ffffff;
            color: #2c3e50;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .container {{
            background: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        h1 {{
            font-size: 22px;
            margin-top: 0;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
            text-align: center;
            letter-spacing: 0.5px;
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
