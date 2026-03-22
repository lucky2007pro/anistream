import os
from pathlib import Path

import requests
from django.core.exceptions import ImproperlyConfigured


TELEGRAM_UPLOAD_LIMIT_BYTES = 2 * 1024 * 1024 * 1024


class TelegramStorageError(Exception):
    """Telegram upload/stream bilan bog'liq xatolar."""


def _get_telegram_config():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
    channel_username = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "").strip().lstrip("@")

    if not token or not channel_id:
        raise ImproperlyConfigured(
            "TELEGRAM_BOT_TOKEN va TELEGRAM_CHANNEL_ID env o'zgaruvchilari to'ldirilishi kerak."
        )

    return token, channel_id, channel_username


def upload_episode_to_telegram(episode):
    """Episode dagi local video faylni Telegram private/public kanalga yuboradi."""
    token, channel_id, channel_username = _get_telegram_config()

    if not episode.video_file:
        raise TelegramStorageError("Telegram'ga yuklash uchun Episode'da video_file bo'lishi kerak.")

    local_path = Path(episode.video_file.path)
    if not local_path.exists():
        raise TelegramStorageError("Episode video fayli serverda topilmadi.")

    file_size = local_path.stat().st_size
    if file_size > TELEGRAM_UPLOAD_LIMIT_BYTES:
        raise TelegramStorageError("Video 2GB limitdan katta. Faylni siqish yoki bo'lib yuklang.")

    send_url = f"https://api.telegram.org/bot{token}/sendDocument"
    caption = f"{episode.anime.title} - {episode.episode_number}-qism"

    with local_path.open("rb") as video_handle:
        response = requests.post(
            send_url,
            data={"chat_id": channel_id, "caption": caption},
            files={"document": video_handle},
            timeout=120,
        )

    if response.status_code != 200:
        raise TelegramStorageError(f"Telegram API xatosi: {response.status_code}")

    payload = response.json()
    if not payload.get("ok"):
        raise TelegramStorageError(f"Telegram API javobi: {payload}")

    result = payload["result"]
    document = result.get("document", {})
    file_id = document.get("file_id")
    message_id = result.get("message_id")

    if not file_id:
        raise TelegramStorageError("Telegram file_id qaytmadi.")

    episode.telegram_file_id = file_id
    episode.telegram_message_id = message_id

    if channel_username and message_id:
        episode.telegram_channel_post_url = f"https://t.me/{channel_username}/{message_id}"

    episode.save(update_fields=["telegram_file_id", "telegram_message_id", "telegram_channel_post_url"])
    return episode


def get_telegram_file_url(file_id):
    """Bot token orqali Telegram file URL qaytaradi."""
    token, _, _ = _get_telegram_config()

    response = requests.get(
        f"https://api.telegram.org/bot{token}/getFile",
        params={"file_id": file_id},
        timeout=30,
    )

    if response.status_code != 200:
        raise TelegramStorageError(f"getFile so'rovi xato: {response.status_code}")

    payload = response.json()
    if not payload.get("ok"):
        raise TelegramStorageError(f"getFile javobi xato: {payload}")

    file_path = payload.get("result", {}).get("file_path")
    if not file_path:
        raise TelegramStorageError("file_path topilmadi.")

    return f"https://api.telegram.org/file/bot{token}/{file_path}"

