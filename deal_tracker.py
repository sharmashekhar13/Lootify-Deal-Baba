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
        print("Telegram Status Code:", response.status_code)
        print("Telegram Response Text:", response.text)
    except Exception as e:
        print(f"Failed to send message: {e}")

def fetch_and_send_deals():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    new_sent_deals = set(sent_deals)
    deals_sent = 0

    # Source 1: RSS2JSON DesiDime Deals
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.desidime.com/deals.rss"
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        if data.get("status") == "ok" and "items" in data:
            for item in data["items"]:
                title = item.get("title", "")
                link = item.get("link", "")
                if link and link not in sent_deals:
                    store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in link.lower() else \
                            "Amazon" if "amazon" in title.lower() or "amazon" in link.lower() else \
                            "Myntra" if "myntra" in title.lower() or "myntra" in link.lower() else \
                            "E-Commerce"

                    msg = f"🚨 *LOOT DEAL ALERT ({store})*\n\n" \
                          f"📦 *Product:* {title}\n" \
                          f"🛒 *Store:* {store}\n\n" \
                          f"🔗 *Direct Link:* [Buy / View Deal]({link})"
                    
                    send_telegram_message(msg)
                    new_sent_deals.add(link)
                    sent_deals.add(link)
                    deals_sent += 1
                    if deals_sent >= 5:
                        break
    except Exception as e:
        print(f"Source 1 error: {e}")

    # Source 2: Reddit Deals India (Fallback)
    if deals_sent < 3:
        try:
            url = "https://www.reddit.com/r/dealsindia/new.json?limit=10"
            resp = requests.get(url, headers=headers, timeout=15)
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                pdata = post.get("data", {})
                title = pdata.get("title", "")
                link = pdata.get("url", "")
                permalink = f"https://reddit.com{pdata.get('permalink', '')}"
                
                target_link = link if link.startswith("http") else permalink

                if target_link and target_link not in sent_deals:
                    store = "Flipkart" if "flipkart" in title.lower() or "flipkart" in target_link.lower() else \
                            "Amazon" if "amazon" in title.lower() or "amazon" in target_link.lower() else \
                            "Deals India"

                    msg = f"🚨 *LOOT DEAL ALERT ({store})*\n\n" \
                          f"📦 *Product:* {title}\n" \
                          f"🛒 *Store:* {store}\n\n" \
                          f"🔗 *Direct Link:* [Buy / View Deal]({target_link})"
                    
                    send_telegram_message(msg)
                    new_sent_deals.add(target_link)
                    sent_deals.add(target_link)
                    deals_sent += 1
                    if deals_sent >= 5:
                        break
        except Exception as e:
            print(f"Source 2 error: {e}")

    print(f"Total deals sent in this execution: {deals_sent}")

    with open(CACHE_FILE, "w") as f:
        json.dump(list(new_sent_deals), f)

if __name__ == "__main__":
    fetch_and_send_deals()
