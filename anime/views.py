
from django.http import JsonResponse
from django.utils import timezone
from .models import ChatMessage, ReelLike, ReelComment, ReelShare, StoryView, Story, Reel
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
import json


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import StreamingHttpResponse
from django.contrib import messages
from django.db.models import Prefetch, Q, Count
from django.core.paginator import Paginator
from .models import (
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
import re

logger = logging.getLogger(__name__)


def staff_required(view_func):
    """
    Faqat staff/superuser foydalanuvchilar uchun ruxsat beruvchi dekorator.
    Login bo'lmaganlar auth sahifaga, oddiy userlar 403 sahifaga qaytariladi.
    """

    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            return HttpResponseForbidden("Sizda bu sahifaga kirish huquqi yo'q.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def home_page(request):
    """Asosiy sahifa - Anime katalog"""
    try:
        all_animes = Anime.objects.all().order_by('-created_at')
        active_stories = Story.objects.filter(is_active=True).order_by('-created_at')
        context = {
            'animes': all_animes,
            'stories': active_stories,
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Home page error: {e}")
        messages.error(request, "Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
        return render(request, 'index.html', {'animes': []})


def anime_detail(request, anime_id):
    """Anime detallari va qismlar"""
    try:
        anime = get_object_or_404(
            Anime.objects.prefetch_related('episodes'),
            id=anime_id
        )
        context = {
            'anime': anime,
        }
        return render(request, 'detail.html', context)
    except Exception as e:
        logger.error(f"Anime detail error: {e}")
        messages.error(request, "Anime topilmadi.")
        return redirect('home')


def reels_page(request):
    """Reels sahifasi"""
    reels_qs = Reel.objects.all().order_by('-created_at')
    
    paginator = Paginator(reels_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'shorts.html', context)


def episode_stream(request, episode_id):
    """Episode videosini stream qiladi."""
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

def auth_view(request):
    """Login va Register sahifasi"""
    if request.method == 'POST':
        action = request.POST.get('action')

        # Ro'yxatdan o'tish
        if action == 'register':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            # Validatsiya
            if not username or not email or not password:
                messages.error(request, "Barcha maydonlarni to'ldiring!")
                return render(request, 'auth.html')

            if len(password) < 6:
                messages.error(request, "Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
                return render(request, 'auth.html')

            # Foydalanuvchi mavjudligini tekshirish
            if User.objects.filter(username=username).exists():
                messages.error(request, "Bu foydalanuvchi nomi allaqachon band!")
                return render(request, 'auth.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Bu email allaqachon ro'yxatdan o'tgan!")
                return render(request, 'auth.html')

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # SHU QATORNI QO'SHISH KERAK:
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user)
                messages.success(request, f"Xush kelibsiz, {username}!")
                logger.info(f"New user registered: {username}")
                return redirect('home')
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, "Ro'yxatdan o'tishda xatolik. Qaytadan urinib ko'ring.")

        # Tizimga kirish
        elif action == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            if not username or not password:
                messages.error(request, "Foydalanuvchi nomi va parolni kiriting!")
                return render(request, 'auth.html')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {username}!")
                logger.info(f"User logged in: {username}")
                return redirect('home')
            else:
                messages.error(request, "Noto'g'ri foydalanuvchi nomi yoki parol!")

    return render(request, 'auth.html')

def catalog_page(request):
    """Katalog - filter va search bilan"""
    animes = Anime.objects.all().prefetch_related('genres')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        animes = animes.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by genre
    genre_slug = request.GET.get('genre', '')
    if genre_slug:
        animes = animes.filter(genres__slug=genre_slug)

    # Filter by type
    anime_type = request.GET.get('type', '')
    if anime_type:
        animes = animes.filter(anime_type=anime_type)

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        animes = animes.filter(status=status)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    animes = animes.order_by(sort_by)

    # Pagination
    paginator = Paginator(animes, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    genres = Genre.objects.all()

    context = {
        'page_obj': page_obj,
        'genres': genres,
        'search_query': search_query,
        'selected_genre': genre_slug,
        'selected_type': anime_type,
        'selected_status': status,
        'selected_sort': sort_by,
    }
    return render(request, 'catalog.html', context)


def genres_page(request):
    """Barcha janrlar"""
    genres = Genre.objects.annotate(anime_count=Count('animes')).order_by('name')
    context = {'genres': genres}
    return render(request, 'genres.html', context)


def genre_detail(request, slug):
    """Janr bo'yicha anime'lar"""
    genre = get_object_or_404(Genre, slug=slug)
    animes = genre.animes.all()

    paginator = Paginator(animes, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'genre': genre,
        'page_obj': page_obj,
    }
    return render(request, 'catalog.html', context)


def schedule_page(request):
    """Haftalik jadval"""
    animes = (
        Anime.objects.filter(status='ongoing')
        .prefetch_related('genres', 'episodes')
        .order_by('-created_at')[:20]
    )
    context = {'animes': animes}
    return render(request, 'schedule.html', context)


def search_page(request):
    """Qidiruv sahifasi"""
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Anime.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(studio__icontains=query)
        ).order_by('-rating')[:20]

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search.html', context)


@login_required
def profile_page(request):
    """User profili"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        avatar_url = request.POST.get('avatar_url', '')

        profile.bio = bio
        if avatar_url:
            profile.avatar_url = avatar_url
        profile.save()

        messages.success(request, "Profil yangilandi!")
        return redirect('profile')

    context = {'profile': profile}
    return render(request, 'profile.html', context)


@login_required
def favorites_page(request):
    """Sevimli anime'lar"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    favorites = profile.favorites.all().order_by('-created_at')

    context = {
        'favorites': favorites,
        'is_watchlist': False,
    }
    return render(request, 'favorites.html', context)


@login_required
def add_to_favorites(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)
    profile = get_object_or_404(UserProfile, user=request.user)

    if anime in profile.favorites.all():
        profile.favorites.remove(anime)
        messages.success(request, f"{anime.title} sevimlilardan olib tashlandi.")
    else:
        profile.favorites.add(anime)
        messages.success(request, f"{anime.title} sevimlilarga qo'shildi.")

    return redirect('detail', anime_id=anime.id)


@login_required
def add_comment(request, anime_id):
    if request.method == "POST":
        anime = get_object_or_404(Anime, id=anime_id)
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                anime=anime,
                user=request.user,
                text=text
            )
            messages.success(request, "Izohingiz qo'shildi!")
        else:
            messages.error(request, "Izoh matni bo'sh bo'lishi mumkin emas.")
        
    return redirect('detail', anime_id=anime_id)


@login_required
def watchlist_page(request):
    """Ko'rish uchun rejalashtirilgan"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    watchlist = profile.watchlist.all().order_by('-created_at')

    context = {
        'favorites': watchlist,
        'is_watchlist': True,
    }
    return render(request, 'favorites.html', context)


@login_required
def history_page(request):
    """Ko'rish tarixi"""
    history = WatchHistory.objects.filter(user=request.user).order_by('-last_watched')[:50]

    context = {'history': history}
    return render(request, 'history.html', context)


@login_required
def settings_page(request):
    """Sozlamalar"""
    if request.method == 'POST':
        email = request.POST.get('email', '')
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, "Sozlamalar saqlandi!")
            return redirect('settings')

    return render(request, 'settings.html')


def news_list(request):
    """Yangiliklar ro'yxati"""
    news = NewsPost.objects.filter(is_published=True).order_by('-created_at')

    paginator = Paginator(news, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'news-list.html', context)


def news_detail(request, slug):
    """Yangilik detali"""
    news = get_object_or_404(NewsPost, slug=slug, is_published=True)

    news.views += 1
    news.save(update_fields=['views'])

    related_news = NewsPost.objects.filter(
        is_published=True
    ).exclude(id=news.id).order_by('-created_at')[:3]

    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'news-detail.html', context)


def about_page(request):
    """Biz haqimizda"""
    return render(request, 'about.html')


def contact_page(request):
    """Bog'lanish"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')

        messages.success(request, "Xabaringiz yuborildi! Tez orada javob beramiz.")
        logger.info(f"Contact form: {name} - {email}")
        return redirect('contact')

    return render(request, 'contact.html')


def faq_page(request):
    """FAQ"""
    return render(request, 'faq.html')


def premium_page(request):
    """Premium"""
    return render(request, 'premium.html')


def fandub_projects_page(request):
    """Fandub loyihalari"""
    return render(request, 'fandub-projects.html')


def live_streams_page(request):
    """Jonli efirlar"""
    return render(request, 'live-streams.html')


@login_required
def billing_page(request):
    """Foydalanuvchi hisob/billing sahifasi"""
    return render(request, 'billing.html')


def password_reset_help_page(request):
    """Parolni tiklash bo'yicha yo'riqnoma sahifasi"""
    return render(request, 'password-reset-help.html')


def custom_404(request, exception=None):
    """404 error page"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """500 error page"""
    return render(request, '500.html', status=500)


@login_required
def logout_view(request):
    """Logout"""
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz")
    return redirect('home')


# ==============================
# Custom admin dashboard views
# ==============================


@staff_required
def admin_dashboard(request):
    """Asosiy admin panel - statistikalar va oxirgi obyektlar"""
    genre_count = Genre.objects.count()
    anime_count = Anime.objects.count()
    episode_count = Episode.objects.count()
    news_count = NewsPost.objects.count()

    latest_animes = Anime.objects.order_by("-created_at")[:5]
    latest_news = NewsPost.objects.order_by("-created_at")[:5]

    context = {
        "genre_count": genre_count,
        "anime_count": anime_count,
        "episode_count": episode_count,
        "news_count": news_count,
        "latest_animes": latest_animes,
        "latest_news": latest_news,
    }
    return render(request, "admin/dashboard.html", context)


# --------- Genre admin ----------


@staff_required
def admin_genre_list(request):
    query = request.GET.get("q", "").strip()
    genres = Genre.objects.all().order_by("name")
    if query:
        genres = genres.filter(Q(name__icontains=query) | Q(slug__icontains=query))

    paginator = Paginator(genres, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/genre_list.html",
        {"page_obj": page_obj, "query": query},
    )


@staff_required
def admin_genre_create(request):
    if request.method == "POST":
        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Janr muvaffaqiyatli qo'shildi.")
            return redirect("admin_genre_list")
    else:
        form = GenreForm()

    return render(
        request,
        "admin/genre_form.html",
        {"form": form, "title": "Yangi janr qo'shish"},
    )


@staff_required
def admin_genre_edit(request, pk):
    genre = get_object_or_404(Genre, pk=pk)

    if request.method == "POST":
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            messages.success(request, "Janr yangilandi.")
            return redirect("admin_genre_list")
    else:
        form = GenreForm(instance=genre)

    return render(
        request,
        "admin/genre_form.html",
        {"form": form, "title": "Janrni tahrirlash"},
    )


@staff_required
def admin_genre_delete(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        genre.delete()
        messages.success(request, "Janr o'chirildi.")
        return redirect("admin_genre_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": genre, "object_type": "Janr", "cancel_url": "admin_genre_list"},
    )


# --------- Anime admin ----------


@staff_required
def admin_anime_list(request):
    query = request.GET.get("q", "").strip()
    animes = Anime.objects.all().order_by("-created_at")
    if query:
        animes = animes.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(studio__icontains=query)
        )

    paginator = Paginator(animes, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/anime_list.html",
        {"page_obj": page_obj, "query": query},
    )


@staff_required
def admin_anime_create(request):
    if request.method == "POST":
        form = AnimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Anime muvaffaqiyatli qo'shildi.")
            return redirect("admin_anime_list")
    else:
        form = AnimeForm()

    return render(
        request,
        "admin/anime_form.html",
        {"form": form, "title": "Yangi anime qo'shish"},
    )


@staff_required
def admin_anime_edit(request, pk):
    anime = get_object_or_404(Anime, pk=pk)

    if request.method == "POST":
        form = AnimeForm(request.POST, instance=anime)
        if form.is_valid():
            form.save()
            messages.success(request, "Anime yangilandi.")
            return redirect("admin_anime_list")
    else:
        form = AnimeForm(instance=anime)

    return render(
        request,
        "admin/anime_form.html",
        {"form": form, "title": "Anime tahrirlash"},
    )


@staff_required
def admin_anime_delete(request, pk):
    anime = get_object_or_404(Anime, pk=pk)
    if request.method == "POST":
        anime.delete()
        messages.success(request, "Anime o'chirildi.")
        return redirect("admin_anime_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": anime, "object_type": "Anime", "cancel_url": "admin_anime_list"},
    )


# --------- Episode admin ----------


@staff_required
def admin_episode_list(request):
    query = request.GET.get("q", "").strip()
    episodes = (
        Episode.objects.select_related("anime")
        .all()
        .order_by("anime__title", "episode_number")
    )
    if query:
        episodes = episodes.filter(
            Q(anime__title__icontains=query) | Q(title__icontains=query)
        )

    paginator = Paginator(episodes, 25)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/episode_list.html",
        {"page_obj": page_obj, "query": query},
    )


@staff_required
def admin_episode_create(request):
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
def admin_episode_delete(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    if request.method == "POST":
        episode.delete()
        messages.success(request, "Qism o'chirildi.")
        return redirect("admin_episode_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": episode, "object_type": "Qism", "cancel_url": "admin_episode_list"},
    )


# --------- News admin ----------


@staff_required
def admin_news_list(request):
    query = request.GET.get("q", "").strip()
    news = NewsPost.objects.select_related("author").all().order_by("-created_at")
    if query:
        news = news.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__icontains=query)
        )

    paginator = Paginator(news, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/news_list_admin.html",
        {"page_obj": page_obj, "query": query},
    )


@staff_required
def admin_news_create(request):
    if request.method == "POST":
        form = NewsPostForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, "Yangilik muvaffaqiyatli qo'shildi.")
            return redirect("admin_news_admin_list")
    else:
        form = NewsPostForm()

    return render(
        request,
        "admin/news_form.html",
        {"form": form, "title": "Yangi yangilik qo'shish"},
    )


@staff_required
def admin_news_edit(request, pk):
    news = get_object_or_404(NewsPost, pk=pk)

    if request.method == "POST":
        form = NewsPostForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangilik yangilandi.")
            return redirect("admin_news_admin_list")
    else:
        form = NewsPostForm(instance=news)

    return render(
        request,
        "admin/news_form.html",
        {"form": form, "title": "Yangilikni tahrirlash"},
    )


@staff_required
def admin_news_delete(request, pk):
    news = get_object_or_404(NewsPost, pk=pk)
    if request.method == "POST":
        news.delete()
        messages.success(request, "Yangilik o'chirildi.")
        return redirect("admin_news_admin_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": news, "object_type": "Yangilik", "cancel_url": "admin_news_admin_list"},
    )

# --------- Reel admin ----------

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
        {"object": short, "object_type": "Reel", "cancel_url": "admin_short_list"},
    )


# --- MIGRATED VIEWS ---

@login_required
def chat(request):
    tz = ZoneInfo('Asia/Tashkent')

    # fetch all messages up to limit
    messages_count = ChatMessage.objects.count()
    has_more = messages_count > 40

    messages_list = list(
        ChatMessage.objects.select_related('user', 'reply_to', 'user__avatar', 'user__vip_data').order_by(
            '-created_at')[:40])
    messages_list.reverse()

    for msg in messages_list:
        msg.local_created_at = localtime(msg.created_at, tz)

    if request.method == "POST":

        if request.user.is_banned:
            messages.error(request, "Siz yozolmaysiz")
            return redirect('chat')

        text = request.POST.get("message", "").strip()
        reply_to_id = request.POST.get("reply_to")
        reply_to_msg = None

        if reply_to_id:
            try:
                reply_to_msg = ChatMessage.objects.get(id=int(reply_to_id))
            except:
                pass

        if text:
            ChatMessage.objects.create(
                user=request.user,
                message=text,
                created_at=timezone.now(),
                reply_to=reply_to_msg
            )

        return redirect('chat')

    return render(request, 'chat.html', {
        'messages': messages_list,
        'has_more': has_more
    })


# =======================
# CHAT API (Load older messages)
# =======================


@login_required
def chat_messages_api(request):
    tz = ZoneInfo('Asia/Tashkent')
    before_id = request.GET.get('before')
    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    qs = ChatMessage.objects.select_related('user', 'user__avatar', 'user__vip_data', 'reply_to').order_by(
        '-created_at')
    if before_id and before_id.isdigit():
        qs = qs.filter(id__lt=before_id)

    messages_list = list(qs[:limit])
    messages_list.reverse()

    data = []
    for msg in messages_list:
        reply_data = None
        if msg.reply_to:
            reply_data = {
                'id': msg.reply_to.id,
                'username': msg.reply_to.user.username,
                'message': msg.reply_to.message
            }

        avatar_url = msg.user.avatar.image.url if getattr(msg.user, 'avatar', None) and msg.user.avatar.image else None

        data.append({
            'id': msg.id,
            'message': msg.message,
            'username': msg.user.username,
            'avatar_url': avatar_url,
            'time': localtime(msg.created_at, tz).strftime('%H:%M'),
            'edited': msg.edited,
            'is_own': msg.user == request.user,
            'is_admin': msg.user.is_admin_user,
            'is_vip': hasattr(msg.user, 'vip_data') and msg.user.vip_data.vip_active(),
            'reply_to': reply_data,
            'can_edit': (msg.user == request.user) or request.user.is_admin_user,
            'can_ban': request.user.is_admin_user and not msg.user.is_admin_user,
            'user_id': msg.user.id
        })

    return JsonResponse({'messages': data})


# =======================
# EDIT MESSAGE
# =======================


@login_required
def edit_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)

    if request.user != msg.user and not request.user.is_admin_user:
        messages.error(request, "Ruxsat yo‘q")
        return redirect('chat')

    if request.method == "POST":
        new_text = request.POST.get("message", "").strip()
        if new_text:
            msg.message = new_text
            msg.edited = True
            msg.save()

    return redirect('chat')


# =======================
# DELETE MESSAGE
# =======================


@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)

    if request.user != msg.user and not request.user.is_admin_user:
        messages.error(request, "Ruxsat yo‘q")
        return redirect('chat')

    msg.delete()
    return redirect('chat')


# =======================
# BAN USER
# =======================


@login_required
def ban_user(request, user_id):
    if not request.user.is_admin_user:
        return redirect('chat')

    user_to_ban = get_object_or_404(CustomUser, id=user_id)

    if not user_to_ban.is_admin_user:
        user_to_ban.is_banned = True
        user_to_ban.save()

    return redirect('chat')


# =======================
# PREMIUM PAGE
# =======================


@login_required
def reels_feed(request):
    latest = Reel.objects.order_by('-created_at').first()
    if latest:
        return redirect('reel_detail', reel_id=latest.id)
    return render(request, 'reels.html', {'reels': [], 'liked_ids': []})




def reel_detail(request, reel_id):
    reel = get_object_or_404(Reel, id=reel_id)
    Reel.objects.filter(id=reel_id).update(views_count=models.F('views_count') + 1)

    # Pastga scroll = eski reel (created_at kichikroq)
    next_reel = Reel.objects.filter(
        created_at__lt=reel.created_at
    ).order_by('-created_at').first()

    # Tepaga scroll = yangi reel (created_at kattaroq)
    prev_reel = Reel.objects.filter(
        created_at__gt=reel.created_at
    ).order_by('created_at').first()

    is_liked = False
    if request.user.is_authenticated:
        is_liked = ReelLike.objects.filter(user=request.user, reel=reel).exists()

    return render(request, 'reel_detail.html', {
        'reel': reel,
        'is_liked': is_liked,
        'total_likes': reel.likes.count(),
        'total_comments': reel.comments.count(),
        'next_reel': next_reel,
        'prev_reel': prev_reel,
    })




# confikuchun viev qismi

BG_COLORS = [
    {'name': 'Qora',           'value': '#0a0a0f',   'css': '#0a0a0f'},
    {'name': 'Qoʻngʻir qora',  'value': '#0d0d0d',   'css': '#0d0d0d'},
    {'name': 'To\'q ko\'k',    'value': '#050d1a',   'css': '#050d1a'},
    {'name': 'Chuqur ko\'k',   'value': '#060b18',   'css': 'linear-gradient(135deg,#060b18,#0a0f22)'},
    {'name': 'Qoʻngʻir',       'value': '#120a06',   'css': '#120a06'},
    {'name': 'Qizil-qora',     'value': '#120a0f',   'css': '#120a0f'},
    {'name': 'Roʻza-qora',     'value': '#180810',   'css': 'linear-gradient(135deg,#180810,#0d0510)'},
    {'name': 'Binafsha-qora',  'value': '#0a0818',   'css': 'linear-gradient(135deg,#0a0818,#120a1f)'},
    {'name': 'Yashil-qora',    'value': '#060f0a',   'css': '#060f0a'},
    {'name': 'Kulrang',        'value': '#101014',   'css': '#101014'},
]




@login_required
def toggle_reel_like(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': reel.likes.count(),
    })




@login_required
def add_reel_comment(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    text = request.POST.get('text', '').strip()
    reply_to_id = request.POST.get('reply_to')

    reply_obj = None
    if reply_to_id:
        try:
            reply_obj = ReelComment.objects.get(id=int(reply_to_id))
        except (ReelComment.DoesNotExist, ValueError):
            reply_obj = None

    if not text:
        return JsonResponse({'error': "Izoh bo'sh bo'lmasin"}, status=400)

    comment = ReelComment.objects.create(
        reel=reel,
        user=request.user,
        text=text,
        reply_to=reply_obj,
    )

    avatar_url = None
    if getattr(request.user, 'avatar', None) and request.user.avatar.image:
        avatar_url = request.user.avatar.image.url

    return JsonResponse({
        'status': 'ok',
        'comment': {
            'id': comment.id,
            'user': request.user.username,
            'text': comment.text,
            'time': comment.created_at.strftime('%H:%M'),
            'avatar': avatar_url,
            'reply_to': reply_obj.id if reply_obj else None,
            'reply_user': reply_obj.user.username if reply_obj else None,
        },
        'total_comments': reel.comments.count(),
    })




@login_required
def reel_comments_api(request, reel_id):
    comments = ReelComment.objects.select_related(
        'user', 'user__avatar', 'reply_to', 'reply_to__user'
    ).filter(reel_id=reel_id).order_by('created_at')

    data = []
    for c in comments:
        avatar_url = None
        if getattr(c.user, 'avatar', None) and c.user.avatar.image:
            avatar_url = c.user.avatar.image.url

        data.append({
            'id': c.id,
            'user': c.user.username,
            'text': c.text,
            'time': c.created_at.strftime('%H:%M'),
            'avatar': avatar_url,
            'reply_to': c.reply_to.id if c.reply_to else None,
            'reply_user': c.reply_to.user.username if c.reply_to else None,
            'reply_text': c.reply_to.text[:40] if c.reply_to else None,
        })

    return JsonResponse({'comments': data})




@login_required
def reel_share(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    ReelShare.objects.create(reel=reel, user=request.user)
    Reel.objects.filter(id=reel_id).update(shares_count=models.F('shares_count') + 1)
    reel.refresh_from_db()

    return JsonResponse({
        'status': 'shared',
        'total_shares': reel.shares_count,
    })




def story_view(request, story_id):
    story = get_object_or_404(Story, id=story_id, is_active=True)

    if story.expires_at and story.expires_at < timezone.now():
        return redirect('home')

    if request.user.is_authenticated:
        StoryView.objects.get_or_create(user=request.user, story=story)

    return render(request, 'story_view.html', {
        'story': story
    })


# =======================
# AJAX: STORY SEEN
# =======================


@login_required
def mark_story_seen(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    obj, created = StoryView.objects.get_or_create(
        user=request.user,
        story=story
    )

    return JsonResponse({
        'status': 'ok',
        'created': created,
        'views_count': story.views.count()
    })



def next_story_view(request, story_id):
    stories = get_story_list()

    for i, s in enumerate(stories):
        if s.id == story_id:
            if i + 1 < len(stories):
                return redirect('story_view', story_id=stories[i + 1].id)
            else:
                return redirect('home')

    return redirect('home')




def prev_story_view(request, story_id):
    stories = get_story_list()

    for i, s in enumerate(stories):
        if s.id == story_id:
            if i - 1 >= 0:
                return redirect('story_view', story_id=stories[i - 1].id)
            else:
                return redirect('home')

    return redirect('home')




# REELS — views.py ga qo'shing
