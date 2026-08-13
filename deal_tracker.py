import os
import re
import json
import requests
import feedparser

# Telegram Credentials from Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CACHE_FILE = "sent_deals.json"

# Load sent deal history to avoid duplicates
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        sent_deals = set(json.load(f))
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
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_and_filter_deals():
    # Deal Feed Aggregators covering Amazon, Flipkart, Myntra, Ajio, Tata CLiQ
    rss_urls = [
        "https://www.desidime.com/deals.rss",
        "https://www.desidime.com/top-deals.rss"
    ]
    
    new_sent_deals = set(sent_deals)
    
    for rss_url in rss_urls:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            summary = entry.get("summary", "")
            
            # Check for discount percentage (75% to 99% off)
            discount_match = re.search(r'(\b[7-9][5-9]%\b|\b90%\b|\b95%\b|\b99%\b|\b80%\b|\b85%\b)', title + " " + summary)
            
            if discount_match and link not in sent_deals:
                # Identify Store Name
                store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in link.lower() else \
                        "Amazon" if "amazon" in title.lower() or "amazon" in link.lower() else \
                        "Myntra" if "myntra" in title.lower() or "myntra" in link.lower() else \
                        "E-Commerce Deal"
                
                # Format Alert
                message = f"🚨 *HEAVY DISCOUNT ALERT ({store})*\n\n" \
                          f"📦 *Product:* {title}\n" \
                          f"🔥 *Discount:* 75%+ OFF\n" \
                          f"🛒 *Store:* {store}\n\n" \
                          f"🔗 *Direct Link:* [Buy / View Deal]({link})"
                
                send_telegram_message(message)
                new_sent_deals.add(link)

    # Save updated deal history
    with open(CACHE_FILE, "w") as f:
        json.dump(list(new_sent_deals), f)

if __name__ == "__main__":
    fetch_and_filter_deals()
