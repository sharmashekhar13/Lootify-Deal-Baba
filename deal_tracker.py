import os
import re
import json
import requests
import feedparser

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram API Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_and_filter_deals():
    rss_urls = [
        "https://www.desidime.com/deals.rss",
        "https://www.desidime.com/top-deals.rss"
    ]
    
    new_sent_deals = set(sent_deals)
    deals_sent = 0
    
    for rss_url in rss_urls:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            if link not in sent_deals:
                store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in link.lower() else \
                        "Amazon" if "amazon" in title.lower() or "amazon" in link.lower() else \
                        "Myntra" if "myntra" in title.lower() or "myntra" in link.lower() else \
                        "E-Commerce Deal"
                
                message = f"🚨 *NEW LOOT DEAL ({store})*\n\n" \
                          f"📦 *Product:* {title}\n" \
                          f"🛒 *Store:* {store}\n\n" \
                          f"🔗 *Direct Link:* [Buy / View Deal]({link})"
                
                send_telegram_message(message)
                new_sent_deals.add(link)
                deals_sent += 1

    print(f"Total new deals sent in this run: {deals_sent}")

    with open(CACHE_FILE, "w") as f:
        json.dump(list(new_sent_deals), f)

if __name__ == "__main__":
    fetch_and_filter_deals()
