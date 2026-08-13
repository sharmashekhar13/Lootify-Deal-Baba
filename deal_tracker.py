import os
import json
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CACHE_FILE = "sent_deals.json"

# Load sent deals cache
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
        print(f"Telegram Status: {response.status_code}")
        print(f"Telegram Response: {response.text}")
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_and_send_deals():
    # RSS-to-JSON API proxy to bypass Datacenter IP blocking
    sources = [
        "https://api.rss2json.com/v1/api.json?rss_url=https://www.desidime.com/deals.rss",
        "https://api.rss2json.com/v1/api.json?rss_url=https://www.desidime.com/top-deals.rss"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    new_sent_deals = set(sent_deals)
    deals_sent = 0

    for source_url in sources:
        try:
            resp = requests.get(source_url, headers=headers, timeout=15)
            data = resp.json()
            
            if data.get("status") == "ok" and "items" in data:
                for item in data["items"]:
                    title = item.get("title", "")
                    link = item.get("link", "")
                    
                    if link and link not in sent_deals:
                        store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in link.lower() else \
                                "Amazon" if "amazon" in title.lower() or "amazon" in link.lower() else \
                                "Myntra" if "myntra" in title.lower() or "myntra" in link.lower() else \
                                "Ajio" if "ajio" in title.lower() or "ajio" in link.lower() else \
                                "E-Commerce Deal"

                        message = f"🚨 *LOOT DEAL ALERT ({store})*\n\n" \
                                  f"📦 *Product:* {title}\n" \
                                  f"🛒 *Store:* {store}\n\n" \
                                  f"🔗 *Direct Link:* [Buy / View Deal]({link})"

                        send_telegram_message(message)
                        new_sent_deals.add(link)
                        sent_deals.add(link)
                        deals_sent += 1

                        if deals_sent >= 5:
                            break
        except Exception as e:
            print(f"Error fetching source {source_url}: {e}")

        if deals_sent >= 5:
            break

    print(f"Total deals sent in this run: {deals_sent}")

    with open(CACHE_FILE, "w") as f:
        json.dump(list(new_sent_deals), f)

if __name__ == "__main__":
    fetch_and_send_deals()
