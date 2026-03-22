import os
import re
import mimetypes
import logging
from django.http import StreamingHttpResponse, HttpResponse
from telethon import utils
from .telegram_client import get_telegram_client

logger = logging.getLogger(__name__)

CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

async def get_telegram_stream_response(request, episode):
    """
    Episode uchun Telegram orqali MTProto stream response qaytaradi.
    Agar client ulanmasa yoki xatolik bo'lsa, None qaytaradi (fallback uchun).
    """
    client = await get_telegram_client()
    if not client or not CHANNEL_ID:
        return None

    try:
        # Kanal ID integer formatda kerak (-100...)
        try:
            channel_id = int(CHANNEL_ID)
        except ValueError:
            logger.error(f"TELEGRAM_CHANNEL_ID noto'g'ri formatda: {CHANNEL_ID}")
            return None
        
        message_id = episode.telegram_message_id
        if not message_id:
            logger.warning(f"Episode {episode.id} da telegram_message_id yo'q.")
            return None

        # Xabarni olish
        message = await client.get_messages(channel_id, ids=message_id)
        if not message or not message.media:
            logger.warning(f"Message {message_id} topilmadi yoki media yo'q.")
            return None

        # Fayl haqida ma'lumot
        file_size = message.file.size
        mime_type = message.file.mime_type or "video/mp4"
        file_name = "video.mp4"
        if message.file.name:
            file_name = message.file.name

        # Range headerni o'qish
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

        # Generator funksiya
        async def file_iterator():
            try:
                async for chunk in client.iter_download(
                    message.media, 
                    offset=offset, 
                    limit=length, 
                    chunk_size=1024 * 1024, # 1MB chunks
                    request_size=512 * 1024 # 512KB requests
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Stream error: {e}")

        response = StreamingHttpResponse(
            file_iterator(),
            status=status_code,
            content_type=mime_type
        )
        
        response['Content-Length'] = str(length)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        
        if content_range:
            response['Content-Range'] = content_range

        return response

    except Exception as e:
        logger.error(f"Telegram stream general error: {e}")
        return None

