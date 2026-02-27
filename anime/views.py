from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Anime


# 1. ASOSIY SAHIFA (Katalog)
def home_page(request):
    all_animes = Anime.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'animes': all_animes})


# 2. ICHKI SAHIFA (Batafsil ma'lumot va qismlar)
def anime_detail(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)
    return render(request, 'detail.html', {'anime': anime})


# 3. AVTORIZATSIYA SAHIFASI (Login va Registratsiya)
def auth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # Qaysi forma jo'natilganini aniqlaymiz

        # Ro'yxatdan o'tish
        if action == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Agar bunday foydalanuvchi bazada yo'q bo'lsa, yangisini yaratamiz
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)  # Yaratilgandan so'ng darhol tizimga kiritamiz
                return redirect('home')  # Asosiy sahifaga jo'natamiz

        # Tizimga kirish
        elif action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Bazadan foydalanuvchini tekshiramiz
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')

    # Agar hech qanday POST bo'lmasa, shunchaki HTML ni ko'rsatamiz
    return render(request, 'auth.html')