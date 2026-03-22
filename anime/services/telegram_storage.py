import os
from pathlib import Path
import logging

import requests
from django.core.exceptions import ImproperlyConfigured


TELEGRAM_UPLOAD_LIMIT_BYTES = 2 * 1024 * 1024 * 1024
logger = logging.getLogger(__name__)


class TelegramStorageError(Exception):
    """Telegram upload/stream bilan bog'liq xatolar."""


class UploadProgressFile:
    """requests uchun fayl oqimini o'qish va progress callback yuborish wrapper."""

    def __init__(self, file_handle, total_size, progress_callback=None):
        self._file_handle = file_handle
        self._total_size = total_size
        self._progress_callback = progress_callback
        self._read_size = 0
        self._last_percent = -1

    def __len__(self):
        return self._total_size

    @property
    def name(self):
        return getattr(self._file_handle, "name", "video.mp4")

    def read(self, size=-1):
        chunk = self._file_handle.read(size)
        if not chunk:
            if self._progress_callback and self._last_percent < 100:
                self._progress_callback(self._total_size, self._total_size)
            return chunk

        self._read_size += len(chunk)
        if self._progress_callback and self._total_size > 0:
            percent = int((self._read_size * 100) / self._total_size)
            # Har 5% da callback yuboramiz.
            if percent >= self._last_percent + 5 or percent == 100:
                self._last_percent = percent
                self._progress_callback(self._read_size, self._total_size)

        return chunk


def _get_telegram_config():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.environ.get("TELEGRAM_CHANNEL_ID", "").strip()
    channel_username = os.environ.get("TELEGRAM_CHANNEL_USERNAME", "").strip().lstrip("@")

    if not token or not channel_id:
        raise ImproperlyConfigured(
            "TELEGRAM_BOT_TOKEN va TELEGRAM_CHANNEL_ID env o'zgaruvchilari to'ldirilishi kerak."
        )

    return token, channel_id, channel_username


def upload_episode_to_telegram(episode, delete_local_file=False, progress_callback=None):
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

    if progress_callback is None:
        def progress_callback(uploaded, total):
            if total <= 0:
                return
            percent = int((uploaded * 100) / total)
            logger.info("Telegram upload progress: %s%% (episode_id=%s)", percent, episode.id)

    with local_path.open("rb") as video_handle:
        monitored_file = UploadProgressFile(video_handle, file_size, progress_callback)
        response = requests.post(
            send_url,
            data={"chat_id": channel_id, "caption": caption},
            files={"document": monitored_file},
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

    update_fields = ["telegram_file_id", "telegram_message_id", "telegram_channel_post_url"]

    if delete_local_file and episode.video_file:
        episode.video_file.delete(save=False)
        episode.video_file = None
        update_fields.append("video_file")

    episode.save(update_fields=update_fields)
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

