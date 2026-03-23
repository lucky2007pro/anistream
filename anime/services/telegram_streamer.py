import os
import re
import asyncio
import logging
from django.http import StreamingHttpResponse, HttpResponse
from asgiref.sync import async_to_sync
from .telegram_client import get_telegram_client

logger = logging.getLogger(__name__)

CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")


class SyncTelethonStreamer:
    """
    Telethon async generatorini Django WSGI (sinxron) uchun moslashtiruvchi sinxron iterator.
    async_to_sync orqali iter_download ning __anext__ metodini bitta standart
    asgiref event loopida xavfsiz chaqiradi.
    Bu orqali cross-thread event loop mismatch xatolari oldi olinadi.
    """
    def __init__(self, client, media, offset, length):
        self.client = client
        self.agen = client.iter_download(
            media,
            offset=offset,
            limit=length,
            chunk_size=512 * 1024,   # 512KB chunks
            request_size=512 * 1024,
        )

    def __iter__(self):
        return self

    def __next__(self):
        # async generatorning keyingi elementini olish uchun coroutine
        async def _get_next_chunk():
            return await self.agen.__anext__()

        try:
            # asgiref.sync.async_to_sync xuddi get_telegram_client chaqirilgan
            # loopni topib, o'sha joyda bajaradi. 
            return async_to_sync(_get_next_chunk)()
        except StopAsyncIteration:
            raise StopIteration
        except Exception as e:
            logger.error(f"Telethon chunk stream xata: {e}")
            raise StopIteration


async def get_telegram_stream_response(request, episode):
    """
    Episode uchun Telegram MTProto stream response qaytaradi.
    Bu funksiya async bo'lib, views.py da async_to_sync() orqali chaqiriladi.
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

    # Asgiref async_to_sync arxitekturasiga mos tushadigan sinxron iterator
    sync_streamer = SyncTelethonStreamer(client, message.media, offset, length)

    response = StreamingHttpResponse(
        sync_streamer,
        status=status_code,
        content_type=mime_type,
    )

    response['Content-Length'] = str(length)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Disposition'] = f'inline; filename="{file_name}"'

    if content_range:
        response['Content-Range'] = content_range

    return response
