import os

with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
i_start = content.find("from .models import (")
i_end = content.find("import requests") + len("import requests")

new_imports = """from .models import (
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

content = content[:i_start] + new_imports + content[i_end:]

# 2. shorts_page to end of episode_stream
s_start = content.find("def shorts_page(request):")
s_end = content.find("def auth_view(request):")

new_streams = """def reels_page(request):
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
    from django.http import HttpResponse, StreamingHttpResponse
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

    return HttpResponse("Video topilmadi.", status=404)

"""

content = content[:s_start] + new_streams + content[s_end:]

# 3. admin_episode_create and edit
c_start = content.find("def admin_episode_create(request):")
c_end = content.find("def admin_episode_delete(request, pk):")

new_admin_episode = """def admin_episode_create(request):
    if request.method == "POST":
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            episode = form.save()
            from django.contrib import messages
            messages.success(request, "Qism muvaffaqiyatli qo'shildi.")
            from django.shortcuts import redirect
            return redirect("admin_episode_list")
    else:
        form = EpisodeForm()

    from django.shortcuts import render
    return render(
        request,
        "admin/episode_form.html",
        {"form": form, "title": "Yangi qism qo'shish"},
    )


@staff_required
def admin_episode_edit(request, pk):
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
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
"""

content = content[:c_start] + new_admin_episode + content[c_end:]

# 4. admin_short_* -> admin_reel_*
sh_start = content.find("# --------- ShortVideo admin ----------")
sh_end = content.find('{"object": short, "object_type": "Lavha (Short)", "cancel_url": "admin_short_list"},')

new_admin_reels = """# --------- Reel admin ----------

@staff_required
def admin_short_list(request):
    query = request.GET.get("q", "").strip()
    reels = Reel.objects.select_related("anime").all().order_by("-created_at")
    if query:
        reels = reels.filter(
            Q(title__icontains=query)
        )

    from django.core.paginator import Paginator
    paginator = Paginator(reels, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    from django.shortcuts import render
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
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.success(request, "Reel muvaffaqiyatli qo'shildi.")
            return redirect("admin_short_list")
    else:
        form = ReelForm()

    animes = Anime.objects.all().order_by('title')

    from django.shortcuts import render
    return render(
        request,
        "admin/short_form.html",
        {"form": form, "title": "Yangi reel qo'shish", "animes": animes},
    )


@staff_required
def admin_short_edit(request, pk):
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
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
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    short = get_object_or_404(Reel, pk=pk)
    if request.method == "POST":
        short.delete()
        messages.success(request, "Reel o'chirildi.")
        return redirect("admin_short_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": short, "object_type": "Reel", "cancel_url": "admin_short_list"},"""

content = content[:sh_start] + new_admin_reels + content[sh_end + len('{"object": short, "object_type": "Lavha (Short)", "cancel_url": "admin_short_list"},'):]

with open('d:/anime/anistream/anime/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Views updated successfully.")
