from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Prefetch
from .models import Anime, Episode
import logging

logger = logging.getLogger(__name__)


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