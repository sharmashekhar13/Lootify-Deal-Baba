import os
import json
import requests
import feedparser

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
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_and_send_deals():
    # User-Agent prevents RSS servers from blocking Python requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    rss_urls = [
        "https://www.desidime.com/deals.rss",
        "https://www.desidime.com/top-deals.rss"
    ]
    
    new_sent_deals = set(sent_deals)
    deals_sent = 0

    for rss_url in rss_urls:
        try:
            # Fetch feed content using Browser User-Agent
            resp = requests.get(rss_url, headers=headers, timeout=15)
            feed = feedparser.parse(resp.content)
            
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                
                # Check if deal is new
                if link not in sent_deals:
                    store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in link.lower() else \
                            "Amazon" if "amazon" in title.lower() or "amazon" in link.lower() else \
                            "Myntra" if "myntra" in title.lower() or "myntra" in link.lower() else \
                            "Ajio" if "ajio" in title.lower() or "ajio" in link.lower() else \
                            "E-Commerce Deal"

                    message = f"🚨 *NEW LOOT DEAL ({store})*\n\n" \
                              f"📦 *Product:* {title}\n" \
                              f"🛒 *Store:* {store}\n\n" \
                              f"🔗 *Direct Link:* [Buy / View Deal]({link})"

                    send_telegram_message(message)
                    new_sent_deals.add(link)
                    sent_deals.add(link)
                    deals_sent += 1

                    # Send up to 5 fresh deals per run
                    if deals_sent >= 5:
                        break
        except Exception as e:
            print(f"Error fetching feed {rss_url}: {e}")

        if deals_sent >= 5:
            break

    print(f"Successfully sent {deals_sent} deals to Telegram.")

    # Save updated cache
    with open(CACHE_FILE, "w") as f:
        json.dump(list(new_sent_deals), f)

if __name__ == "__main__":
    fetch_and_send_deals()
