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
import requests

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
        context = {
            'animes': all_animes,
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


def shorts_page(request):
    """Lavhalar va qisqa videolar sahifasi"""
    shorts_qs = ShortVideo.objects.all().order_by('-created_at')
    
    paginator = Paginator(shorts_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'shorts.html', context)


def short_stream(request, short_id):
    """Telegram file'ni brauzerga stream qiladi (Range/seek qo'llab-quvvatlanadi). Kichik lavhalar uchun."""
    try:
        short_video = ShortVideo.objects.get(id=short_id)
    except ShortVideo.DoesNotExist:
        return HttpResponse("Lavha topilmadi", status=404)

    if not short_video.telegram_file_id:
        return HttpResponseBadRequest("Bu lavhada Telegram file_id mavjud emas.")

    try:
        file_url = get_telegram_file_url(short_video.telegram_file_id)
    except TelegramStorageError as exc:
        return HttpResponse(
            f"TELEGRAM_STREAM_ERROR: {exc}",
            status=502,
            content_type='text/plain; charset=utf-8',
        )

    outbound_headers = {}
    range_header = request.headers.get('Range') or request.META.get('HTTP_RANGE')
    if range_header:
        outbound_headers['Range'] = range_header

    try:
        tg_response = requests.get(
            file_url,
            headers=outbound_headers,
            stream=True,
            timeout=90,
        )
    except requests.RequestException as exc:
        return HttpResponse(
            f"TELEGRAM_NETWORK_ERROR: {exc}",
            status=502,
            content_type='text/plain; charset=utf-8',
        )

    if tg_response.status_code not in (200, 206):
        return HttpResponse(
            f"TELEGRAM_UPSTREAM_ERROR: {tg_response.status_code}",
            status=tg_response.status_code if tg_response.status_code in (400, 401, 403, 404, 416) else 502,
            content_type='text/plain; charset=utf-8',
        )

    stream = StreamingHttpResponse(
        tg_response.iter_content(chunk_size=1024 * 1024),
        content_type=tg_response.headers.get('Content-Type', 'application/octet-stream'),
        status=tg_response.status_code,
    )

    if tg_response.headers.get('Content-Range'):
        stream['Content-Range'] = tg_response.headers['Content-Range']
    if tg_response.headers.get('Content-Length'):
        stream['Content-Length'] = tg_response.headers['Content-Length']
    if tg_response.headers.get('Accept-Ranges'):
        stream['Accept-Ranges'] = tg_response.headers['Accept-Ranges']
    else:
        stream['Accept-Ranges'] = 'bytes'

    stream['Content-Disposition'] = f'inline; filename="short-{short_video.id}.mp4"'
    stream['Cache-Control'] = 'public, max-age=3600'
    return stream


async def episode_stream(request, episode_id):
    """Episode videosini stream qiladi. telegram_message_id bo'lsa MTProto, bo'lmasa Bot API orqali."""
    from asgiref.sync import sync_to_async
    try:
        from django.shortcuts import get_object_or_404
        episode = await sync_to_async(get_object_or_404)(Episode, id=episode_id)
    except Exception:
        return HttpResponse(status=404)

    # 1. MTProto stream (Large files, recommended)
    if episode.telegram_message_id:
        try:
            # get_telegram_stream_response is async
            response = await get_telegram_stream_response(request, episode)
            if response:
                return response
        except Exception as e:
            logger.error(f"MTProto stream error: {e}")

    # 2. Bot API stream (Small files < 20MB)
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
                    if tg_response.headers.get('Content-Range'):
                        stream['Content-Range'] = tg_response.headers['Content-Range']
                    if tg_response.headers.get('Content-Length'):
                        stream['Content-Length'] = tg_response.headers['Content-Length']
                    
                    stream['Accept-Ranges'] = 'bytes'
                    stream['Content-Disposition'] = f'inline; filename="episode-{episode.id}.mp4"'
                    return stream
            response = await sync_to_async(get_bot_api_stream)()
            if response:
                return response
        except Exception as e:
            logger.error(f"Bot API stream error: {e}")

    return HttpResponse("Video stream qilib bo'lmadi", status=404)


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
            
            # Telegram'ga yuklash
            upload_to_tg = form.cleaned_data.get('upload_to_telegram')
            delete_local = form.cleaned_data.get('delete_local_after_upload')
            
            if upload_to_tg and episode.video_file:
                try:
                    upload_episode_to_telegram(episode, delete_local_file=delete_local)
                    messages.success(request, "Qism muvaffaqiyatli qo'shildi va Telegram'ga yuklandi.")
                except TelegramStorageError as e:
                    messages.warning(request, f"Qism qo'shildi, lekin Telegram'ga yuklashda xato: {e}")
            else:
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
            
            # Telegram'ga yuklash
            upload_to_tg = form.cleaned_data.get('upload_to_telegram')
            delete_local = form.cleaned_data.get('delete_local_after_upload')
            
            if upload_to_tg and episode.video_file:
                try:
                    upload_episode_to_telegram(episode, delete_local_file=delete_local)
                    messages.success(request, "Qism yangilandi va Telegram'ga yuklandi.")
                except TelegramStorageError as e:
                    messages.warning(request, f"Qism yangilandi, lekin Telegram'ga yuklashda xato: {e}")
            else:
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

# --------- ShortVideo admin ----------

@staff_required
def admin_short_list(request):
    query = request.GET.get("q", "").strip()
    shorts = ShortVideo.objects.select_related("anime").all().order_by("-created_at")
    if query:
        shorts = shorts.filter(
            Q(title__icontains=query)
        )

    paginator = Paginator(shorts, 20)
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
        form = ShortVideoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lavha muvaffaqiyatli qo'shildi.")
            return redirect("admin_short_list")
    else:
        form = ShortVideoForm()

    animes = Anime.objects.all().order_by('title')

    return render(
        request,
        "admin/short_form.html",
        {"form": form, "title": "Yangi lavha qo'shish", "animes": animes},
    )


@staff_required
def admin_short_edit(request, pk):
    short = get_object_or_404(ShortVideo, pk=pk)

    if request.method == "POST":
        form = ShortVideoForm(request.POST, instance=short)
        if form.is_valid():
            form.save()
            messages.success(request, "Lavha yangilandi.")
            return redirect("admin_short_list")
    else:
        form = ShortVideoForm(instance=short)

    animes = Anime.objects.all().order_by('title')

    return render(
        request,
        "admin/short_form.html",
        {"form": form, "short": short, "title": "Lavhani tahrirlash", "animes": animes},
    )


@staff_required
def admin_short_delete(request, pk):
    short = get_object_or_404(ShortVideo, pk=pk)
    if request.method == "POST":
        short.delete()
        messages.success(request, "Lavha o'chirildi.")
        return redirect("admin_short_list")

    return render(
        request,
        "admin/confirm_delete.html",
        {"object": short, "object_type": "Lavha (Short)", "cancel_url": "admin_short_list"},
    )
