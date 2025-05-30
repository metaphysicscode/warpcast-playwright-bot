import os
import time
import asyncio
from playwright.async_api import async_playwright
import requests
from dotenv import load_dotenv

load_dotenv()

USERS = os.getenv("WARPCAST_USERS", "").split(",")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 5))

last_seen = {}

async def get_latest_cast(playwright, username):
    try:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://warpcast.com/{username.strip()}", timeout=15000)
        await page.wait_for_selector("main", timeout=10000)
        content = await page.text_content("main")
        await browser.close()
        return content.strip() if content else None
    except Exception as e:
        print(f"[{username}] Error: {e}")
        return None

def send_to_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Telegram Error: {e}")

async def main():
    print("✅ Warpcast Telegram Bot with Playwright started...")
    async with async_playwright() as playwright:
        while True:
            for user in USERS:
                print(f"Checking user: {user}")
                cast = await get_latest_cast(playwright, user)
                if cast and (user not in last_seen or last_seen[user] != cast):
                    msg = f"[{user}] {cast[:280]}"
                    print(msg)
                    send_to_telegram(msg)
                    last_seen[user] = cast
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
