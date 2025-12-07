import asyncio
import feedparser
import json
import os
import html
import hashlib
from telegram import Bot
from telegram.constants import ParseMode
from urllib.parse import urlparse
import re

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 180  # 3 minutes – fast & safe

# Your original feeds (with site/platform parsing)
FEEDS = [
    # G4SKINS
    {"name": "G4SKINS: Facebook", "url": "https://rss.app/feed/L1WdCH7lKcgWyFP4"},
    {"name": "G4SKINS: Instagram", "url": "https://rss.app/feed/0ytCa0QQWhu6Mjgb"},
    {"name": "G4SKINS: Twitter", "url": "https://rss.app/feed/hRn71mvapExinyaC"},
    
    # CSGOSKINS
    {"name": "CSGOSKINS: Facebook", "url": "https://rss.app/feed/A4NhJ7dwo9MGGP10"},
    {"name": "CSGOSKINS: Instagram", "url": "https://rss.app/feed/9j17jbrplI2VNYkU"},
    {"name": "CSGOSKINS: Twitter", "url": "https://rss.app/feed/M22b0ZoyZeR43T67"},

    # CSGOCASES
    {"name": "CSGOCASES: Facebook", "url": "https://rss.app/feed/qpjnqFC4Yqhsgwqy"},
    {"name": "CSGOCASES: Instagram", "url": "https://rss.app/feed/hGPhFovsEWjtX370"},
    {"name": "CSGOCASES: Twitter", "url": "https://rss.app/feed/uXaPnasrtzpUrQVq"},
]

HISTORY_FILE = "sent_posts.json"

# Fake User-Agent for rss.app
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_history(s):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(list(s)[-2000:], f)

def get_id(e, url):
    return e.get('id') or e.get('guid') or e.get('link') or hashlib.md5((e.get('title', '') + e.get('published', '') + url).encode()).hexdigest()

def parse_feed_name(feed_name):
    """Extract Site and Platform from feed name like 'G4SKINS: Instagram'"""
    match = re.match(r'(.+?):\s*(.+)', feed_name.strip())
    if match:
        return match.group(1), match.group(2)
    return feed_name, "Unknown"

def get_post_text(entry):
    """Get full post text: title + description/summary"""
    title = entry.get('title', '') or ''
    desc = entry.get('description', '') or entry.get('summary', '') or ''
    # Clean HTML from desc
    desc = re.sub(r'<[^>]+>', '', desc).strip()[:500]  # First 500 chars
    return f"{title}\n\n{desc}" if desc else title

def get_image_url(entry):
    """Extract first image URL from media/enclosures"""
    # Check media content
    if entry.media_content:
        for media in entry.media_content:
            if media.get('medium') == 'image':
                return media.get('url')
    # Check enclosures
    if entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href')
    return None

async def send_notification(bot, feed_conf, entry):
    site, platform = parse_feed_name(feed_conf['name'])
    post_text = get_post_text(entry)
    image_url = get_image_url(entry)
    link = entry.get('link', '')

    # Base message format
    message = (
        f"<b>Site:</b> {html.escape(site)}\n"
        f"<b>Platform:</b> {html.escape(platform)}\n\n"
        f"<b>Post:</b>\n{html.escape(post_text)}\n\n"
    )
    if link:
        message += f"<a href='{link}'>🔗 Open Full Post</a>"

    try:
        if image_url:
            # Send as photo with caption
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=image_url,
                caption=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            print(f"Sent PHOTO notification: {site} {platform}")
        else:
            # Send as text
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            print(f"Sent TEXT notification: {site} {platform}")
    except Exception as e:
        print(f"Telegram send failed: {e}")

async def main():
    print("CS2 Socials Farming Bot STARTED (Enhanced Notifications)")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Test message
    await asyncio.sleep(3)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Bot updated! Now with Site/Platform/Post/Image format. 🔔", parse_mode=ParseMode.HTML)
    
    history = load_history()
    first_run = True

    while True:
        print(f"\nChecking {len(FEEDS)} feeds... (Interval: {CHECK_INTERVAL}s)")
        for feed_conf in FEEDS:
            try:
                parsed = feedparser.parse(feed_conf['url'])
                print(f"  {feed_conf['name']} → {len(parsed.entries)} entries")

                for entry in parsed.entries[:5]:
                    pid = get_id(entry, feed_conf['url'])
                    if pid not in history:
                        if not first_run:
                            await send_notification(bot, feed_conf, entry)
                        history.add(pid)
            except Exception as e:
                print(f"  Feed error {feed_conf['name']}: {e}")

        save_history(history)
        if first_run:
            print("First run done – only NEW posts from now on")
            first_run = False

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")