import os
import json
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8864579611:AAHXfBbUXvvbumfhZgOwWC0x1u5iGJX_Lrc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "-1003960961427")
CACHE_FILE = "sent_deals.json"

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            sent_deals = set(json.load(f))
    except Exception:
        sent_deals = set()
else:
    sent_deals = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=12)
        print(f"Telegram API Status: {response.status_code}")
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
    return "E-Commerce Loot"

def fetch_and_send_deals():
    reddit_headers = {"User-Agent": "LootifyDealBot/1.0"}
    browser_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    deals_collected = []

    # Fetch from Reddit Deals India
    try:
        res = requests.get("https://www.reddit.com/r/dealsindia/new.json?limit=25", headers=reddit_headers, timeout=10)
        if res.status_code == 200:
            for p in res.json().get("data", {}).get("children", []):
                data = p.get("data", {})
                title = data.get("title", "").strip()
                link = data.get("url", "").strip()
                if title and link:
                    deals_collected.append((title, link))
    except Exception as e:
        print(f"Reddit Error: {e}")

    # Fetch from DesiDime RSS
    try:
        res = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fwww.desidime.com%2Fdeals.rss", headers=browser_headers, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("items", []):
                title = item.get("title", "").strip()
                link = item.get("link", "").strip()
                if title and link:
                    deals_collected.append((title, link))
    except Exception as e:
        print(f"DesiDime Error: {e}")

    unique_deals = []
    seen_links = set(sent_deals)
    for t, l in deals_collected:
        if l not in seen_links:
            seen_links.add(l)
            unique_deals.append((t, l))

    sent_count = 0
    new_sent_deals = set(sent_deals)

    for title, link in unique_deals[:5]:
        store = get_store_name(title, link)
        message = f"🚨 *HEAVY DISCOUNT LOOT DEAL ({store})*\n\n" \
                  f"📦 *Product:* {title}\n" \
                  f"🛒 *Store:* {store}\n\n" \
                  f"🔗 *Direct Link:* [Buy / View Deal]({link})"
        
        send_telegram_message(message)
        new_sent_deals.add(link)
        sent_count += 1

    print(f"Successfully sent {sent_count} deal alerts to Telegram.")

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(list(new_sent_deals), f)
    except Exception as e:
        print(f"Cache save note: {e}")

if __name__ == "__main__":
    fetch_and_send_deals()
