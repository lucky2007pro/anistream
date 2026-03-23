import os
import re
import asyncio
import queue
import threading
import logging
from django.http import StreamingHttpResponse, HttpResponse
from .telegram_client import get_telegram_client

logger = logging.getLogger(__name__)

CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# Sentinel: iter tugaganini bildiradi
_DONE = object()
# Sentinel: xato yuz berganini bildiradi
_ERROR = object()


def _run_async_download(coro, chunk_queue):
    """
    Yangi eventloop da async coroutine ishlatadi va
    chunklarni sinxron queue ga qo'yadi.
    Bu alohida threadda chaqiriladi.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro(chunk_queue))
    except Exception as e:
        chunk_queue.put((_ERROR, e))
    finally:
        loop.close()


def _make_sync_generator(chunk_queue):
    """
    Queue dan chunklar olib sinxron generator sifatida yield qiladi.
    """
    while True:
        item = chunk_queue.get()
        if item is _DONE:
            break
        if isinstance(item, tuple) and item[0] is _ERROR:
            logger.error(f"Stream thread xato: {item[1]}")
            break
        yield item


async def get_telegram_stream_response(request, episode):
    """
    Episode uchun Telegram MTProto stream response qaytaradi.
    
    Bu funksiya async bo'lib, views.py da async_to_sync() orqali chaqiriladi.
    Katta fayllar uchun thread+queue yondashuvi ishlatiladi:
    - Telethon async download alohida threadda ishlaydi
    - Django StreamingHttpResponse sinxron generator bilan ishlaydi
    - RAM da butun fayl saqlanmaydi (true streaming)
    """
    client = await get_telegram_client()
    if not client:
        return None

    if not CHANNEL_ID:
        logger.error("TELEGRAM_CHANNEL_ID sozlanmagan.")
        return None

    try:
        channel_id = int(CHANNEL_ID)
    except ValueError:
        logger.error(f"TELEGRAM_CHANNEL_ID noto'g'ri formatda: {CHANNEL_ID}")
        return None

    message_id = episode.telegram_message_id
    if not message_id:
        logger.warning(f"Episode {episode.id} da telegram_message_id yo'q.")
        return None

    try:
        message = await client.get_messages(channel_id, ids=message_id)
    except Exception as e:
        logger.error(f"get_messages xato: {e}")
        return None

    if not message or not message.media:
        logger.warning(f"Message {message_id} topilmadi yoki media yo'q.")
        return None

    # Fayl meta-ma'lumotlari
    file_size = message.file.size
    mime_type = message.file.mime_type or "video/mp4"
    file_name = message.file.name or "video.mp4"

    # Range header
    range_header = request.headers.get('Range')
    offset = 0
    length = file_size
    status_code = 200
    content_range = None

    if range_header:
        range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

            if start >= file_size:
                return HttpResponse(status=416)

            offset = start
            length = end - start + 1
            status_code = 206
            content_range = f"bytes {start}-{end}/{file_size}"

    # Capture variables for the async download coroutine
    _client = client
    _media = message.media
    _offset = offset
    _length = length

    async def _download_to_queue(chunk_queue):
        """Telethon iter_download'dan chunklar olib queue ga qo'yadi."""
        try:
            async for chunk in _client.iter_download(
                _media,
                offset=_offset,
                limit=_length,
                chunk_size=512 * 1024,    # 512KB - brauzer uchun optimal
                request_size=512 * 1024,
            ):
                chunk_queue.put(chunk)
        except Exception as e:
            chunk_queue.put((_ERROR, e))
        finally:
            chunk_queue.put(_DONE)

    # Thread + Queue: async download sinxron generatorga "ko'prik"
    chunk_queue = queue.Queue(maxsize=8)  # 8 * 512KB = 4MB buffer

    download_thread = threading.Thread(
        target=_run_async_download,
        args=(_download_to_queue, chunk_queue),
        daemon=True,
    )
    download_thread.start()

    response = StreamingHttpResponse(
        _make_sync_generator(chunk_queue),
        status=status_code,
        content_type=mime_type,
    )

    response['Content-Length'] = str(length)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Disposition'] = f'inline; filename="{file_name}"'

    if content_range:
        response['Content-Range'] = content_range

    return response
