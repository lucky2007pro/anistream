import re

with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace imports
import_old = """from .models import (
    Anime,
    Episode,
    Genre,
    UserProfile,
    WatchHistory,
    Comment,
    NewsPost,
    ShortVideo,
)
from .forms import GenreForm, AnimeForm, EpisodeForm, NewsPostForm, ShortVideoForm
from .services.telegram_storage import (
    TelegramStorageError,
    get_telegram_file_url,
    upload_episode_to_telegram,
)
from asgiref.sync import async_to_sync, sync_to_async
from .services.telegram_streamer import get_telegram_stream_response
import logging
import requests"""

import_new = """from .models import (
    Anime,
    Episode,
    Genre,
    UserProfile,
    WatchHistory,
    Comment,
    NewsPost,
    Reel,
)
from .forms import GenreForm, AnimeForm, EpisodeForm, NewsPostForm, ReelForm
import logging
import os
import re"""

content = content.replace(import_old, import_new)

# 2. Replace shorts_page, short_stream and episode_stream
# I will use regex to find shorts_page to end of episode_stream
pattern = re.compile(r'def shorts_page.*?return HttpResponse\("Video stream qilib bo\'lmadi o\'rnatilgan manbalardan yo\'q.", status=404\)', re.DOTALL)

replacement = r"""def reels_page(request):
    \"\"\"Reels sahifasi\"\"\"
    reels_qs = Reel.objects.all().order_by('-created_at')
    
    paginator = Paginator(reels_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'shorts.html', context)


def episode_stream(request, episode_id):
    \"\"\"Episode videosini stream qiladi.\"\"\"
    from django.shortcuts import get_object_or_404
    episode = get_object_or_404(Episode, id=episode_id)

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

    return HttpResponse("Video topilmadi.", status=404)"""

# Fix escape issue
replacement = replacement.replace('\\"', '"').replace('\\d', r'\d').replace('\\n', '\n')

content = pattern.sub(replacement, content)

# 3. Replace admin_episode_create and admin_episode_edit

pattern2 = re.compile(r'def admin_episode_create.*?def admin_episode_delete', re.DOTALL)
replacement2 = r"""def admin_episode_create(request):
    if request.method == "POST":
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            episode = form.save()
            messages.success(request, "Qism muvaffaqiyatli qo'shildi.")
            return redirect("admin_episode_list")
    else:
        form = EpisodeForm()

    return render(
        request,
        "admin/episode_form.html",
        {"form": form, "title": "Yangi qism qo'shish"},
    )


@staff_required
def admin_episode_edit(request, pk):
    episode = get_object_or_404(Episode, pk=pk)

    if request.method == "POST":
        form = EpisodeForm(request.POST, request.FILES, instance=episode)
        if form.is_valid():
            episode = form.save()
            messages.success(request, "Qism yangilandi.")
            return redirect("admin_episode_list")
    else:
        form = EpisodeForm(instance=episode)

    return render(
        request,
        "admin/episode_form.html",
        {"form": form, "title": "Qismni tahrirlash"},
    )


@staff_required
def admin_episode_delete"""

content = pattern2.sub(replacement2, content)

# 4. Replace ShortVideo admin views with Reel admin views
pattern3 = re.compile(r'# --------- ShortVideo admin ----------.*?admin_short_list"\)', re.DOTALL)

replacement3 = r"""# --------- Reel admin ----------

@staff_required
def admin_short_list(request):
    query = request.GET.get("q", "").strip()
    reels = Reel.objects.select_related("anime").all().order_by("-created_at")
    if query:
        reels = reels.filter(
            Q(title__icontains=query)
        )

    paginator = Paginator(reels, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/short_list.html",
        {"page_obj": page_obj, "query": query},
    )

@staff_required
def admin_short_create(request):
    if request.method == "POST":
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Reel muvaffaqiyatli qo'shildi.")
            return redirect("admin_short_list")
    else:
        form = ReelForm()

    animes = Anime.objects.all().order_by('title')

    return render(
        request,
        "admin/short_form.html",
        {"form": form, "title": "Yangi reel qo'shish", "animes": animes},
    )

@staff_required
def admin_short_edit(request, pk):
    short = get_object_or_404(Reel, pk=pk)

    if request.method == "POST":
        form = ReelForm(request.POST, request.FILES, instance=short)
        if form.is_valid():
            form.save()
            messages.success(request, "Reel yangilandi.")
            return redirect("admin_short_list")
    else:
        form = ReelForm(instance=short)

    animes = Anime.objects.all().order_by('title')

    return render(
        request,
        "admin/short_form.html",
        {"form": form, "short": short, "title": "Reel tahrirlash", "animes": animes},
    )

@staff_required
def admin_short_delete(request, pk):
    short = get_object_or_404(Reel, pk=pk)
    if request.method == "POST":
        short.delete()
        messages.success(request, "Reel o'chirildi.")
        return redirect("admin_short_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": short, "object_type": "Reel", "cancel_url": "admin_short_list"}"""

content = pattern3.sub(replacement3, content)

with open('d:/anime/anistream/anime/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Views updated successfully.")
