import os
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

API_ID = os.environ.get("TELEGRAM_API_ID")
API_HASH = os.environ.get("TELEGRAM_API_HASH")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING", "")

_client = None

async def get_telegram_client():
    """Singleton Telegram client qaytaradi."""
    global _client
    if _client and _client.is_connected():
        return _client

    if not API_ID or not API_HASH:
        logger.warning("TELEGRAM_API_ID yoki TELEGRAM_API_HASH topilmadi. Streaming ishlamasligi mumkin.")
        return None

    try:
        if SESSION_STRING:
            session = StringSession(SESSION_STRING)
        else:
            session = "django_bot_session"
            
        _client = TelegramClient(session, int(API_ID), API_HASH)
        await _client.start(bot_token=BOT_TOKEN)
        return _client
    except Exception as e:
        logger.error(f"Telegram client error: {e}")
        return None

