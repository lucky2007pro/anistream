# 🎬 AniStream - Professional Anime Streaming Platform

Modern va professional anime streaming platformasi. Django 6.0 asosida yaratilgan.

## ✨ Xususiyatlar

- 🎥 **Video Streaming** - Professional video pleyer
- 📱 **Responsive Design** - Barcha ekranlarda ishlaydi
- 🔐 **User Authentication** - Ro'yxatdan o'tish va kirish tizimi
- 💬 **Comments System** - Har bir anime uchun chat
- 📊 **Admin Panel** - Kuchli boshqaruv paneli
- 🎨 **Modern UI/UX** - Zamonaviy va chiroyli dizayn
- ⚡ **Fast Performance** - Tez va samarali

## 🚀 Texnologiyalar

- **Backend**: Django 6.0.2
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Render.com
- **Static Files**: WhiteNoise
- **Server**: Gunicorn

## 📦 O'rnatish (Local Development)

### 1. Repository ni clone qiling

```bash
git clone https://github.com/yourusername/AniDev.git
cd AniDev
```

### 2. Virtual environment yarating

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Dependencies o'rnating

```bash
pip install -r requirements.txt
```

### 4. Environment variables sozlang

`.env` fayl yarating va quyidagilarni qo'shing:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

# Telegram storage (ixtiyoriy)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_CHANNEL_USERNAME=your_channel_username
```

### 5. Database migrate qiling

```bash
python manage.py migrate
```

### 6. Superuser yarating

```bash
python manage.py createsuperuser
```

### 7. Serverni ishga tushiring

```bash
python manage.py runserver
```

Sayt `http://127.0.0.1:8000/` da ochiladi.

## 🌐 Render.com ga Deploy qilish

### 1. GitHub'ga push qiling

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Render.com'da Web Service yarating

1. [render.com](https://render.com) ga kiring
2. **New** > **Web Service** ni tanlang
3. GitHub repository ni ulang
4. Quyidagi sozlamalarni kiriting:

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn core.wsgi:application
```

### 3. Environment Variables qo'shing

Render.com dashboard'da:

```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://... (avtomatik qo'shiladi)
```

### 4. PostgreSQL Database yarating

1. **New** > **PostgreSQL** ni tanlang
2. Web Service'ga ulang

### 5. Deploy qiling

**Deploy** tugmasini bosing va kuting!

## 📁 Proyekt Strukturasi

```
AniDev/
├── anime/                 # Asosiy app
│   ├── models.py         # Anime va Episode modellari
│   ├── views.py          # Views
│   ├── admin.py          # Admin panel
│   └── templates/        # HTML templates
│       ├── index.html    # Bosh sahifa
│       ├── detail.html   # Anime detallari
│       └── auth.html     # Login/Register
├── core/                 # Project settings
│   ├── settings.py       # Sozlamalar
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI config
├── media/               # Upload qilingan fayllar
├── static/              # Static files
├── requirements.txt     # Python dependencies
├── build.sh            # Render build script
├── runtime.txt         # Python versiyasi
└── .env.example        # Environment example

```

## 🔧 Admin Panel

Admin panelga kirish: `http://your-domain.com/admin/`

### Anime qo'shish:

1. Admin panelga kiring
2. **Animes** > **Add Anime** ni tanlang
3. Ma'lumotlarni kiriting:
   - Title (Anime nomi)
   - Description (Tavsif)
   - Release Year (Chiqgan yili)
   - Rating (Reyting)
   - Image URL (Rasm havolasi)

### Episode qo'shish:

1. **Episodes** > **Add Episode** ni tanlang
2. Anime tanlang
3. Episode raqami kiriting
4. Video yuklang yoki URL kiriting

## Telegram orqali video saqlash

Admin episode formasida `Saqlashdan keyin Telegram kanalga yuklash` ni belgilasangiz, local `video_file` bot orqali kanalga yuboriladi va `telegram_file_id` bazaga saqlanadi.

- Botni private kanalga admin qiling.
- `TELEGRAM_CHANNEL_ID` private kanal ID bo'lishi kerak (`-100...`).
- Pleyer Telegram saqlangan qism uchun `episodes/<id>/stream/` endpoint orqali avtomatik oqim ochadi.

CLI orqali ham yuklash mumkin:

```bash
python manage.py upload_episode_to_telegram 15
```

## 🎨 Customization

### Dizaynni o'zgartirish:

Templates: `anime/templates/`
- `index.html` - Bosh sahifa
- `detail.html` - Anime sahifasi
- `auth.html` - Login sahifasi

### Ranglarni o'zgartirish:

CSS o'zgaruvchilar (har bir template ichida):

```css
:root {
    --accent: #ff3366;        /* Asosiy rang */
    --bg-base: #0f0f13;       /* Fon rangi */
    --text-light: #ffffff;    /* Matn rangi */
}
```

## 🔒 Security Features

- ✅ Environment variables
- ✅ CSRF protection
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ Secure cookies (HTTPS)
- ✅ Password hashing
- ✅ HSTS headers

## 📝 To-Do List

- [ ] Search funksiyasi
- [ ] Favorites tizimi
- [ ] User profiles
- [ ] Social login (Google, Facebook)
- [ ] Email verification
- [ ] Payment integration
- [ ] Mobile app

## 🤝 Contributing

Pull requests are welcome! Katta o'zgarishlar uchun avval issue oching.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Django Framework
- Render.com
- Google Fonts (Outfit)
- Unsplash (Rasmlar)

---

⭐ Agar loyiha yoqsa, star bering!
