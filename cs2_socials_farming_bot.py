# cs2_socials_farming_bot.py  ←  DEBUG VERSION THAT CANNOT FAIL
import asyncio
import feedparser
import json
import os
import html
import hashlib
from telegram import Bot

# ================= PUT YOUR REAL VALUES HERE =================
TELEGRAM_BOT_TOKEN = "8211593813:AAFrW1X-VNci98aWeGXFM4jAn9qkfEqh73A"   # ← YOUR BOT TOKEN
TELEGRAM_CHAT_ID   = "303629260"                                 # ← YOUR CHAT ID (or your private chat ID)
# ==============================================================

CHECK_INTERVAL = 180
HISTORY_FILE = "sent_posts.json"

# Force a normal browser User-Agent (critical for rss.app and many others)
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"

# Ultra-fast test feeds (post every few seconds)
FEEDS = [
#     # --- G4SKINS ---
    {"name": "G4SKINS: Facebook",       "url": "https://rss.app/feed/L1WdCH7lKcgWyFP4"},
    {"name": "G4SKINS: Instagram",      "url": "https://rss.app/feed/0ytCa0QQWhu6Mjgb"},
    {"name": "G4SKINS: Twitter",        "url": "https://rss.app/feed/hRn71mvapExinyaC"},
    
#     # --- CSGOSKINS ---
    {"name": "CSGOSKINS: Facebook",     "url": "https://rss.app/feed/A4NhJ7dwo9MGGP10"},
    {"name": "CSGOSKINS: Instagram",    "url": "https://rss.app/feed/9j17jbrplI2VNYkU"},
    {"name": "CSGOSKINS: Twitter",      "url": "https://rss.app/feed/M22b0ZoyZeR43T67"},

#     # --- CSGOCASES ---
    {"name": "CSGOCASES: Facebook",     "url": "https://rss.app/feed/qpjnqFC4Yqhsgwqy"},
    {"name": "CSGOCASES: Instagram",    "url": "https://rss.app/feed/hGPhFovsEWjtX370"},
    {"name": "CSGOCASES: Twitter",      "url": "https://rss.app/feed/uXaPnasrtzpUrQVq"},
]

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
    return e.get('id') or e.get('link') or hashlib.md5((e.get('title','') + e.get('published','')).encode()).hexdigest()

async def send(bot, text):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode='HTML', disable_web_page_preview=True)
        print("Telegram message SENT successfully")
    except Exception as e:
        print("TELEGRAM SEND FAILED → Check token & chat_id !!!")
        print(f"Error: {e}")

async def main():
    print("STARTING – Sending test message in 3 seconds...")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # GUARANTEED TEST MESSAGE
    await asyncio.sleep(3)
    await send(bot, "Bot is ALIVE and working!\nIf you see this → everything is fine.\nNow checking feeds every 30 sec...")

    history = load_history()
    first_run = True

    while True:
        print(f"\nChecking {len(FEEDS)} feeds... {asyncio.get_event_loop().time():.0f}")
        for feed in FEEDS:
            try:
                parsed = feedparser.parse(feed["url"])
                print(f"  {feed['name']} → {len(parsed.entries)} entries")

                for entry in parsed.entries[:5]:
                    pid = get_id(entry, feed["url"])
                    if pid not in history:
                        title = html.escape(entry.title[:200]) if entry.get('title') else "No title"
                        link = entry.get('link', '')
                        msg = f"<b>{feed['name']}</b>\n{title}"
                        if link:
                            msg += f"\n<a href='{link}'>View →</a>"
                        await send(bot, msg)
                        history.add(pid)
                        print(f"  → NEW POST SENT: {title[:50]}")
            except Exception as e:
                print(f"  Feed error: {e}")

        save_history(history)
        if first_run:
            print("First run done – from now on only NEW posts")
            first_run = False

        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")

# import asyncio
# import feedparser
# import json
# import os
# import html
# from telegram import Bot

# # ================= CONFIGURATION =================
# # 1. Get this from @BotFather
# TELEGRAM_BOT_TOKEN = "8211593813:AAFrW1X-VNci98aWeGXFM4jAn9qkfEqh73A"

# # 2. Get this by sending a message to @userinfobot or checking logs
# TELEGRAM_CHAT_ID = "303629260"

# # How often to check for updates (in seconds). 
# # Don't go lower than 300 (5 mins) to avoid getting rate-limited by RSS.app
# CHECK_INTERVAL = 305

# # Your Feed List
# FEEDS = [
#     # --- G4SKINS ---
#     {"name": "G4SKINS: Facebook",       "url": "https://rss.app/feed/L1WdCH7lKcgWyFP4"},
#     {"name": "G4SKINS: Instagram",      "url": "https://rss.app/feed/0ytCa0QQWhu6Mjgb"},
#     {"name": "G4SKINS: Twitter",        "url": "https://rss.app/feed/hRn71mvapExinyaC"},
    
#     # --- CSGOSKINS ---
#     {"name": "CSGOSKINS: Facebook",     "url": "https://rss.app/feed/A4NhJ7dwo9MGGP10"},
#     {"name": "CSGOSKINS: Instagram",    "url": "https://rss.app/feed/9j17jbrplI2VNYkU"},
#     {"name": "CSGOSKINS: Twitter",      "url": "https://rss.app/feed/M22b0ZoyZeR43T67"},

#     # --- CSGOCASES ---
#     {"name": "CSGOCASES: Facebook",     "url": "https://rss.app/feed/qpjnqFC4Yqhsgwqy"},
#     {"name": "CSGOCASES: Instagram",    "url": "https://rss.app/feed/hGPhFovsEWjtX370"},
#     {"name": "CSGOCASES: Twitter",      "url": "https://rss.app/feed/uXaPnasrtzpUrQVq"},
#     # {"name": "TEST: Nitter X", "url": "https://nitter.cz/ThePSF/rss"},
# ]

# # File to store IDs of posts we have already seen
# HISTORY_FILE = "sent_posts.json"

# # ================= LOGIC =================

# def load_history():
#     """Loads the list of already sent post IDs."""
#     if os.path.exists(HISTORY_FILE):
#         try:
#             with open(HISTORY_FILE, 'r') as f:
#                 return set(json.load(f))
#         except (json.JSONDecodeError, ValueError):
#             return set()
#     return set()

# def save_history(history_set):
#     """Saves the list of sent post IDs (keeping file size manageable)."""
#     # Convert set to list, keep only last 1000 entries to prevent file bloat
#     data = list(history_set)[-1000:]
#     with open(HISTORY_FILE, 'w') as f:
#         json.dump(data, f)

# async def send_notification(bot, feed_name, entry):
#     """Formats and sends the message to Telegram."""
#     title = html.escape(entry.get('title', 'No Title'))
#     link = entry.get('link', '')
    
#     # Construct message
#     message = (
#         f"🔔 <b>New Update: {feed_name}</b>\n\n"
#         f"{title}\n\n"
#         f"<a href='{link}'>Open Post</a>"
#     )

#     try:
#         print(f"Sending: {feed_name} - {title[:20]}...")
#         await bot.send_message(
#             chat_id=TELEGRAM_CHAT_ID, 
#             text=message, 
#             parse_mode='HTML'
#         )
#     except Exception as e:
#         print(f"Failed to send Telegram message: {e}")

# async def main():
#     print("🤖 Social Monitor Bot Started...")
    
#     # Initialize Bot
#     bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
#     # Load history so we don't spam old posts on restart
#     history = load_history()
    
#     # First run flag (optional: set to True if you want to skip sending 
#     # everything currently on the feed and only send NEW things from now on)
#     first_run = False 

#     while True:
#         try:
#             print(f"Checking {len(FEEDS)} feeds...")
            
#             for feed_conf in FEEDS:
#                 try:
#                     # Parse the RSS feed
#                     d = feedparser.parse(feed_conf['url'])
                    
#                     print(f"  -> Entries found: {len(d.entries)}")

#                     if not d.entries:
#                         continue

#                     # Look at the newest entry (index 0)
#                     # Some feeds might have multiple new items, so we can iterate 
#                     # the first 3 just to be safe
#                     for entry in d.entries[:3]:
#                         # Use 'id' if available, otherwise 'link' as unique identifier
#                         post_id = entry.get('id', entry.get('link'))
                        
#                         print(f"  -> Latest post ID: {post_id}")

#                         if post_id and post_id not in history:
#                             if not first_run:
#                                 await send_notification(bot, feed_conf['name'], entry)
                            
#                             history.add(post_id)
                
#                 except Exception as e:
#                     print(f"Error reading feed {feed_conf['name']}: {e}")
            
#             # Save history after checking all feeds
#             save_history(history)
            
#             if first_run:
#                 print("First run complete. History populated. Waiting for new posts...")
#                 first_run = False

#             # Wait before next check
#             await asyncio.sleep(CHECK_INTERVAL)

#         except KeyboardInterrupt:
#             print("Bot stopped by user.")
#             break
#         except Exception as e:
#             print(f"Critical Error in main loop: {e}")
#             await asyncio.sleep(60)

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import feedparser
# import json
# import os
# import html
# from telegram import Bot
# import hashlib

# # ================= CONFIGURATION =================
# TELEGRAM_BOT_TOKEN = "8211593813:AAFrW1X-VNci98aWeGXFM4jAn9qkfEqh73A"

# # 2. Get this by sending a message to @userinfobot or checking logs
# TELEGRAM_CHAT_ID = "303629260"

# # How often to check for updates (in seconds). 
# # Don't go lower than 300 (5 mins) to avoid getting rate-limited by RSS.app
# CHECK_INTERVAL = 5

# # Your Feed List
# # FEEDS = [
# #     # --- G4SKINS ---
# #     # {"name": "G4SKINS: Facebook",       "url": "https://rss.app/feed/L1WdCH7lKcgWyFP4"},
# #     # {"name": "G4SKINS: Instagram",      "url": "https://rss.app/feed/0ytCa0QQWhu6Mjgb"},
# #     # {"name": "G4SKINS: Twitter",        "url": "https://rss.app/feed/hRn71mvapExinyaC"},
    
# #     # # --- CSGOSKINS ---
# #     # {"name": "CSGOSKINS: Facebook",     "url": "https://rss.app/feed/A4NhJ7dwo9MGGP10"},
# #     # {"name": "CSGOSKINS: Instagram",    "url": "https://rss.app/feed/9j17jbrplI2VNYkU"},
# #     # {"name": "CSGOSKINS: Twitter",      "url": "https://rss.app/feed/M22b0ZoyZeR43T67"},

# #     # # --- CSGOCASES ---
# #     # {"name": "CSGOCASES: Facebook",     "url": "https://rss.app/feed/qpjnqFC4Yqhsgwqy"},
# #     # {"name": "CSGOCASES: Instagram",    "url": "https://rss.app/feed/hGPhFovsEWjtX370"},
# #     # {"name": "CSGOCASES: Twitter",      "url": "https://rss.app/feed/uXaPnasrtzpUrQVq"},
# #     # {"name": "TEST: Nitter X", "url": "https://nitter.cz/ThePSF/rss"},
# #     # {"name": "ULTRAFAST: GitHub Trending Python", "url": "https://rsshub.app/github/trending/daily/python"},
# #     {"name": "INSTANT TEST: Crypto Panic", "url": "https://cryptopanic.com/news/rss/"},
# # ]

# FEEDS = [
#     {"name": "TEST → Hacker News",              "url": "https://news.ycombinator.com/rss"},
#     {"name": "TEST → Reddit /r/memes (very fast)", "url": "https://www.reddit.com/r/memes/.rss"},
#     {"name": "TEST → CryptoPanic (posts every 10–20 sec)", "url": "https://cryptopanic.com/news/rss/"},
# ]

# HISTORY_FILE = "sent_posts.json"

# # CRITICAL: Fake browser User-Agent
# feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"

# def load_history():
#     if os.path.exists(HISTORY_FILE):
#         try:
#             with open(HISTORY_FILE, 'r') as f:
#                 return set(json.load(f))
#         except:
#             return set()
#     return set()

# def save_history(history_set):
#     data = list(history_set)[-2000:]  # keep last 2000
#     with open(HISTORY_FILE, 'w') as f:
#         json.dump(data, f)

# def get_unique_id(entry, feed_url):
#     """Robust unique identifier"""
#     id_val = entry.get('id') or entry.get('guid') or entry.get('link', '')
#     if id_val and len(id_val) > 10:
#         return id_val.strip()
    
#     # Fallback: hash of title + published date + feed
#     title = (entry.get('title') or '').strip()
#     pub = entry.get('published') or entry.get('updated') or ''
#     combo = f"{feed_url}{title}{pub}"
#     return hashlib.md5(combo.encode('utf-8')).hexdigest()

# async def send_notification(bot, feed_name, entry):
#     title = html.escape(entry.get('title', 'No Title')[:200])
#     link = entry.get('link', '').strip()

#     message = f"🔔 <b>New from {feed_name}</b>\n\n{title}"
#     if link:
#         message += f"\n\n<a href='{link}'>📱 View Post</a>"

#     try:
#         await bot.send_message(
#             chat_id=TELEGRAM_CHAT_ID,
#             text=message,
#             parse_mode='HTML',
#             disable_web_page_preview=True
#         )
#         print(f"Sent: {feed_name}")
#     except Exception as e:
#         print(f"Telegram send failed: {e}")

# async def main():
#     print("Social Media → Telegram Monitor STARTED")
#     bot = Bot(token=TELEGRAM_BOT_TOKEN)
#     history = load_history()
#     first_run = True

#     while True:
#         try:
#             new_found = False
#             for feed_conf in FEEDS:
#                 try:
#                     # This header bypasses rss.app blocking
#                     d = feedparser.parse(feed_conf['url'])

#                     if not d.entries:
#                         continue

#                     for entry in d.entries[:5]:  # check up to 5 newest
#                         post_id = get_unique_id(entry, feed_conf['url'])

#                         if post_id not in history:
#                             if not first_run:
#                                 await send_notification(bot, feed_conf['name'], entry)
#                                 new_found = True
#                             history.add(post_id)

#                 except Exception as e:
#                     print(f"Feed error {feed_conf['name']}: {e}")

#             save_history(history)

#             if first_run and new_found:
#                 print("First run complete. Now only sending *new* posts.")
#             first_run = False

#             await asyncio.sleep(CHECK_INTERVAL)

#         except KeyboardInterrupt:
#             print("\nStopped by user.")
#             break
#         except Exception as e:
#             print(f"Main loop error: {e}")
#             await asyncio.sleep(60)

# if __name__ == "__main__":
#     asyncio.run(main())


