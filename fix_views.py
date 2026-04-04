import re

# 1. Update models.py get_video_source()
with open(r'd:\AniDev\anime\models.py', 'r', encoding='utf-8') as f:
    models_content = f.read()

models_old = '''    def get_video_source(self):
        if self.telegram_message_id:
            return reverse('episode_stream', args=[self.id])
        if self.telegram_file_id:
            return reverse('episode_stream', args=[self.id])
        if self.video_file:
            try:
                if self.video_file.storage.exists(self.video_file.name):
                    return self.video_file.url
            except Exception:
                pass
        if self.video_url:
            return self.video_url
        return ""'''

models_new = '''    def get_video_source(self):
        if self.telegram_message_id or self.telegram_file_id or self.video_file:
            # We push all media through episode_stream to enable progressive loading (Accept-Ranges) correctly
            return reverse('episode_stream', args=[self.id])
        if self.video_url:
            return self.video_url
        return ""'''

if models_old in models_content:
    models_content = models_content.replace(models_old, models_new)
    with open(r'd:\AniDev\anime\models.py', 'w', encoding='utf-8') as f:
        f.write(models_content)
    print("Updated models.py")
else:
    print("Could not find models_old in models.py")


# 2. Update views.py episode_stream()
with open(r'd:\AniDev\anime\views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# We'll use a regex to replace episode_stream function
start_idx = views_content.find('async def episode_stream(request, episode_id):')
end_idx = views_content.find('def auth_view(request):')

if start_idx != -1 and end_idx != -1:
    views_new = '''async def episode_stream(request, episode_id):
    """Episode videosini stream qiladi. Backend, MTProto va Bot API orqali progressiv yuklash (Range) qollab-quvvatlanadi."""
    from asgiref.sync import sync_to_async
    import os
    import re
    try:
        from django.shortcuts import get_object_or_404
        episode = await sync_to_async(get_object_or_404)(Episode, id=episode_id)
    except Exception:
        return HttpResponse("Episode topilmadi", status=404)

    # 1. Local video_file stream (Supports Range requests for progressive playback)
    if episode.video_file:
        try:
            video_path = episode.video_file.path
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                range_header = request.headers.get('Range') or request.META.get('HTTP_RANGE')
                start_byte = 0
                end_byte = file_size - 1
                status_code = 200
                content_range = None

                if range_header:
                    range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
                    if range_match:
                        start_byte = int(range_match.group(1))
                        end_byte = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                        if start_byte >= file_size:
                            return HttpResponse(status=416)
                        status_code = 206
                        content_range = f'bytes {start_byte}-{end_byte}/{file_size}'
                
                length = end_byte - start_byte + 1

                def file_iterator():
                    with open(video_path, 'rb') as f:
                        f.seek(start_byte)
                        bytes_left = length
                        while bytes_left > 0:
                            chunk_size = min(1024 * 1024, bytes_left)
                            data = f.read(chunk_size)
                            if not data:
                                break
                            bytes_left -= len(data)
                            yield data

                stream = StreamingHttpResponse(
                    file_iterator(),
                    content_type='video/mp4',
                    status=status_code
                )
                stream['Content-Length'] = str(length)
                stream['Accept-Ranges'] = 'bytes'
                stream['Content-Disposition'] = f'inline; filename="episode-{episode.id}.mp4"'
                stream['Cache-Control'] = 'public, max-age=3600'
                if content_range:
                    stream['Content-Range'] = content_range
                return stream
        except Exception as e:
            logger.error(f"Local stream error: {e}")

    # 2. MTProto stream (Large files, recommended)
    if episode.telegram_message_id:
        try:
            response = await get_telegram_stream_response(request, episode)
            if response:
                return response
        except Exception as e:
            logger.error(f"MTProto stream error: {e}")

    # 3. Bot API stream (Small files < 20MB)
    if episode.telegram_file_id:
        try:
            def get_bot_api_stream():
                file_url = get_telegram_file_url(episode.telegram_file_id)
                outbound_headers = {}
                range_header = request.headers.get('Range') or request.META.get('HTTP_RANGE')
                if range_header:
                    outbound_headers['Range'] = range_header

                tg_response = requests.get(
                    file_url,
                    headers=outbound_headers,
                    stream=True,
                    timeout=90,
                )

                if tg_response.status_code in (200, 206):
                    stream = StreamingHttpResponse(
                        tg_response.iter_content(chunk_size=1024 * 1024),
                        content_type=tg_response.headers.get('Content-Type', 'video/mp4'),
                        status=tg_response.status_code,
                    )
                    stream['Accept-Ranges'] = 'bytes'
                    stream['Content-Disposition'] = f'inline; filename="episode-{episode.id}.mp4"'
                    stream['Cache-Control'] = 'public, max-age=3600'
                    
                    if tg_response.headers.get('Content-Range'):
                        stream['Content-Range'] = tg_response.headers['Content-Range']
                    if tg_response.headers.get('Content-Length'):
                        stream['Content-Length'] = tg_response.headers['Content-Length']
                    return stream
            
            response = await sync_to_async(get_bot_api_stream)()
            if response:
                return response
        except Exception as e:
            logger.error(f"Bot API stream error: {e}")

    return HttpResponse("Video stream qilib bo'lmadi o'rnatilgan manbalardan yo'q.", status=404)

'''
    views_content = views_content[:start_idx] + views_new + views_content[end_idx:]
    with open(r'd:\AniDev\anime\views.py', 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("Updated views.py")
else:
    print("Could not find start or end token in views.py")
