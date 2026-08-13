import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Post Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def get_store_name(title, link):
    text = (title + " " + link).lower()
    if "flipkart" in text:
        return "Flipkart"
    elif "amazon" in text:
        return "Amazon"
    elif "myntra" in text:
        return "Myntra"
    elif "ajio" in text:
        return "Ajio"
    elif "meesho" in text:
        return "Meesho"
    elif "tatacliq" in text:
        return "Tata CLiQ"
    return "E-Commerce Loot"

def fetch_and_send_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    deals_collected = []
    
    # Source 1: RSS2JSON DesiDime Deals
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.desidime.com/deals.rss"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get("items", [])
            for item in items[:5]:
                title = item.get("title", "").strip()
                link = item.get("link", "").strip()
                if title and link:
                    deals_collected.append((title, link))
    except Exception as e:
        print(f"Source 1 error: {e}")

    # Source 2: Reddit Deals India JSON
    try:
        url = "https://www.reddit.com/r/dealsindia/new.json?limit=10"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            posts = res.json().get("data", {}).get("children", [])
            for p in posts:
                data = p.get("data", {})
                title = data.get("title", "").strip()
                link = data.get("url", "").strip()
                if title and link:
                    deals_collected.append((title, link))
    except Exception as e:
        print(f"Source 2 error: {e}")

    print(f"Total deals fetched: {len(deals_collected)}")

    # Send top 5 deals directly to Telegram
    sent_count = 0
    for title, link in deals_collected[:5]:
        store = get_store_name(title, link)
        message = f"🚨 *LOOT DEAL ALERT ({store})*\n\n" \
                  f"📦 *Product:* {title}\n" \
                  f"🛒 *Store:* {store}\n\n" \
                  f"🔗 *Direct Link:* [Buy / View Deal]({link})"
        
        send_telegram_message(message)
        sent_count += 1

    print(f"Successfully sent {sent_count} deal alerts to Telegram.")

if __name__ == "__main__":
    fetch_and_send_deals()
