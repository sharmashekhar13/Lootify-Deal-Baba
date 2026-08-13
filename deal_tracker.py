import os
import json
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
        response = requests.post(url, json=payload, timeout=12)
        print(f"Telegram API Status Code: {response.status_code}")
        print(f"Telegram Response: {response.text}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

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
    reddit_headers = {
        "User-Agent": "LootifyDealBot/1.0 (by /u/sharmashekhar13)"
    }
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    deals_collected = []

    # Source 1: Reddit Deals India
    try:
        url = "https://www.reddit.com/r/dealsindia/new.json?limit=25"
        res = requests.get(url, headers=reddit_headers, timeout=10)
        print(f"Source 1 Status: {res.status_code}")
        if res.status_code == 200:
            posts = res.json().get("data", {}).get("children", [])
            for p in posts:
                data = p.get("data", {})
                title = data.get("title", "").strip()
                link = data.get("url", "").strip()
                permalink = f"https://reddit.com{data.get('permalink', '')}"
                target_link = link if link.startswith("http") and "reddit.com" not in link else permalink
                
                if title and target_link:
                    deals_collected.append((title, target_link))
    except Exception as e:
        print(f"Source 1 Error: {e}")

    # Source 2: DesiDime Deals via rss2json
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fwww.desidime.com%2Fdeals.rss"
        res = requests.get(url, headers=browser_headers, timeout=10)
        print(f"Source 2 Status: {res.status_code}")
        if res.status_code == 200:
            items = res.json().get("items", [])
            for item in items:
                title = item.get("title", "").strip()
                link = item.get("link", "").strip()
                if title and link:
                    deals_collected.append((title, link))
    except Exception as e:
        print(f"Source 2 Error: {e}")

    # Source 3: Reddit IndianGaming Deals
    try:
        url = "https://www.reddit.com/r/IndianGaming/new.json?limit=25"
        res = requests.get(url, headers=reddit_headers, timeout=10)
        print(f"Source 3 Status: {res.status_code}")
        if res.status_code == 200:
            posts = res.json().get("data", {}).get("children", [])
            for p in posts:
                data = p.get("data", {})
                title = data.get("title", "").strip()
                link = data.get("url", "").strip()
                permalink = f"https://reddit.com{data.get('permalink', '')}"
                target_link = link if link.startswith("http") and "reddit.com" not in link else permalink
                
                if title and target_link and any(kw in title.lower() for kw in ["deal", "sale", "off", "price"]):
                    deals_collected.append((title, target_link))
    except Exception as e:
        print(f"Source 3 Error: {e}")

    # Deduplicate while preserving order
    unique_deals = []
    seen_links = set()
    for t, l in deals_collected:
        if l not in seen_links:
            seen_links.add(l)
            unique_deals.append((t, l))

    print(f"Total unique deals fetched: {len(unique_deals)}")

    # Send top 5 deals directly to Telegram
    sent_count = 0
    for title, link in unique_deals[:5]:
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
