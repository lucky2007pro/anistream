# ☁️ Cloudinary + Neon.tech Sozlash Qo'llanmasi

Bu qo'llanma sizga **Cloudinary** (media files) va **Neon.tech** (database) bilan ishlashni o'rgatadi.

---

## 📦 ARXITEKTURA

```
┌─────────────────┐
│  Render.com     │  ← Web Hosting (Django app)
│  (Web Service)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Neon   │ │ Cloudinary   │
│ (DB)   │ │ (Media)      │
└────────┘ └──────────────┘
```

- **Render.com**: Django app hosting
- **Neon.tech**: PostgreSQL database (BEPUL, DOIMIY)
- **Cloudinary**: Rasm va video fayllar (25 GB bepul)

---

## 1️⃣ NEON.TECH SOZLASH (Database)

### Nima uchun Neon?
- ✅ **Bepul va doimiy** (muddati tugamaydi)
- ✅ **500 MB** storage (loyihangiz uchun kifoya)
- ✅ **Tez va ishonchli**
- ✅ **PostgreSQL 16**

### Qadamma-qadam:

**1. Akkaunt yarating:**
- https://neon.tech ga kiring
- **Sign up with GitHub** tugmasini bosing

**2. Project yarating:**
- **Create a project** tugmasini bosing
- Project name: `anistream`
- Region: **AWS Asia Pacific (Singapore)** (yoki Frankfurt)
- PostgreSQL version: **16**
- **Create project** tugmasini bosing

**3. Connection String oling:**

Dashboard'da **Connection Details** bo'limida:

```
Connection string:
postgresql://username:password@ep-cool-sound-123456.us-east-2.aws.neon.tech/anistream?sslmode=require
```

**Nusxalab oling!** Bu sizning `DATABASE_URL` bo'ladi.

---

## 2️⃣ CLOUDINARY SOZLASH (Media Files)

### Nima uchun Cloudinary?
- ✅ **25 GB** bepul storage
- ✅ **Rasm optimizatsiya** (avtomatik)
- ✅ **Video streaming**
- ✅ **CDN** (tez yuklash)
- ✅ **Transformatsiya** (resize, crop, etc.)

### Qadamma-qadam:

**1. Akkaunt yarating:**
- https://cloudinary.com ga kiring
- **Sign Up Free** tugmasini bosing
- Email bilan ro'yxatdan o'ting

**2. Dashboard'ga kiring:**

Dashboard'da siz ushbu ma'lumotlarni ko'rasiz:

```
Cloud Name: dxxxxxx
API Key: 123456789012345
API Secret: xXxXxXxXxXxXxXxXxXxXxXxX
```

**Bu uchta qiymatni nusxalab oling!**

**3. Media Library:**
- **Media Library** bo'limiga o'ting
- **Upload** orqali test rasm yuklang
- Yuklangan rasmning URL'ini ko'ring (avtomatik beriladi)

---

## 3️⃣ RENDER.COM SOZLASH

### Environment Variables qo'shing:

Render Dashboard > Web Service > **Environment** tabida:

```env
# Django
SECRET_KEY=django-insecure-bu-joyga-yangi-secret-key-qoying-1234567890
DEBUG=False
ALLOWED_HOSTS=anistream.onrender.com
PYTHON_VERSION=3.12.0

# Database (Neon.tech)
DATABASE_URL=postgresql://username:password@ep-cool-sound-123456.us-east-2.aws.neon.tech/anistream?sslmode=require

# Cloudinary
CLOUDINARY_CLOUD_NAME=dxxxxxx
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=xXxXxXxXxXxXxXxXxXxXxXxX
USE_CLOUDINARY=True
```

### SECRET_KEY generatsiya:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4️⃣ DEPLOY QILING

**1. GitHub'ga push:**
```bash
git add .
git commit -m "Cloudinary va Neon.tech qo'shildi"
git push origin main
```

**2. Render'da deploy:**
- Render avtomatik ravishda yangi commit'ni detect qiladi
- Yoki **Manual Deploy** > **Deploy latest commit**
- ⏳ 5-10 daqiqa kuting

**3. Logs'ni kuzating:**
```
Installing cloudinary...
Installing django-cloudinary-storage...
Collecting static files...
Running migrations...
Starting server...
✅ Your service is live!
```

---

## 5️⃣ ADMIN PANELDA TEST QILING

**1. Superuser yarating:**
- Render Dashboard > **Shell** tab
```bash
python manage.py createsuperuser
```

**2. Admin panelga kiring:**
- https://anistream.onrender.com/admin/

**3. Anime qo'shing:**
- **Animes** > **Add Anime**
- **Image URL** maydoni: Cloudinary'dan rasm URL
- Yoki **Video File** yuklang (Cloudinary'ga avtomatik yuklanadi)

**4. Episode qo'shing:**
- **Episodes** > **Add Episode**
- **Video File** yuklang → Cloudinary'ga avtomatik yuklanadi!

---

## 6️⃣ CLOUDINARY'DA FAYLLARNI KO'RISH

**1. Cloudinary Dashboard:**
- https://console.cloudinary.com
- **Media Library** tabiga o'ting

**2. Yuklangan fayllar:**
- Barcha yuklangan rasm va videolar bu yerda
- Har bir faylning URL'i avtomatik yaratiladi

**3. Transformatsiya (ixtiyoriy):**
```
Asl rasm:
https://res.cloudinary.com/dxxxxxx/image/upload/v1234567890/sample.jpg

Resize qilingan (300x400):
https://res.cloudinary.com/dxxxxxx/image/upload/w_300,h_400,c_fill/v1234567890/sample.jpg
```

---

## 7️⃣ NEON.TECH DATABASE BOSHQARISH

**1. Neon Dashboard:**
- https://console.neon.tech
- Loyihangizni tanlang

**2. SQL Editor:**
- **SQL Editor** tabida to'g'ridan-to'g'ri SQL query ishlatish mumkin

**3. Monitoring:**
- **Monitoring** tabida:
  - Database size
  - Connection count
  - Query performance

**4. Backup (avtomatik):**
- Neon avtomatik ravishda backup oladi
- 7 kun saqlanadi (bepul tier)

---

## 🎯 AFZALLIKLAR

### Cloudinary:
✅ **25 GB** bepul
✅ **Tez CDN**
✅ **Avtomatik optimizatsiya**
✅ **Video streaming**
✅ **Transformatsiya**

### Neon.tech:
✅ **Doimiy bepul** (muddati yo'q)
✅ **500 MB** storage
✅ **Tez va ishonchli**
✅ **Branching** (git kabi)
✅ **Avtomatik backup**

### Render.com:
✅ **750 soat/oy** bepul
✅ **Avtomatik SSL**
✅ **GitHub integration**
✅ **Easy deploy**

---

## 🐛 TROUBLESHOOTING

### Cloudinary'ga yuklanmayapti:

**1. Environment variables tekshiring:**
```bash
# Render Shell'da:
echo $CLOUDINARY_CLOUD_NAME
echo $CLOUDINARY_API_KEY
```

**2. Logs tekshiring:**
```
Cloudinary connection error: Invalid credentials
```
→ API_KEY yoki API_SECRET noto'g'ri

### Neon.tech connection error:

**1. DATABASE_URL to'g'riligini tekshiring:**
- `?sslmode=require` qo'shilganligini tekshiring
- Username va password to'g'ri ekanligini tekshiring

**2. IP whitelist:**
- Neon barcha IP'larni qabul qiladi (whitelist kerak emas)

### Rasmlar ko'rinmayapti:

**1. MEDIA_URL sozlamalari:**
```python
# settings.py da:
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

**2. Template'da:**
```html
<img src="{{ anime.image_url }}" alt="{{ anime.title }}">
```

---

## 📊 MONITORING

### Cloudinary Usage:
- Dashboard > **Usage**
- Storage: XX / 25 GB
- Transformations: XX / 25,000
- Bandwidth: XX GB

### Neon Usage:
- Dashboard > **Settings** > **Usage**
- Storage: XX / 500 MB
- Compute hours: XX / unlimited

### Render Usage:
- Dashboard > **Usage**
- Hours: XX / 750

---

## 💡 TIPS

### Rasm optimizatsiya:
```python
# Cloudinary avtomatik optimizatsiya qiladi
# Quality va format avtomatik sozlanadi
```

### Video streaming:
```html
<!-- Cloudinary video player -->
<video controls>
    <source src="{{ episode.video_file.url }}" type="video/mp4">
</video>
```

### Database backup:
```bash
# Neon avtomatik backup oladi
# Manual backup (ixtiyoriy):
pg_dump DATABASE_URL > backup.sql
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Neon.tech akkaunt yaratildi
- [ ] Cloudinary akkaunt yaratildi
- [ ] Render Environment Variables qo'shildi
- [ ] Deploy muvaffaqiyatli
- [ ] Admin panel ishlayapti
- [ ] Rasm yuklash ishlayapti
- [ ] Video yuklash ishlayapti
- [ ] Database connection ishlayapti

---

## 🎉 TAYYOR!

Endi sizda:
- ✅ **Bepul va doimiy** PostgreSQL database (Neon.tech)
- ✅ **25 GB** media storage (Cloudinary)
- ✅ **Professional** hosting (Render.com)
- ✅ **SSL certificate** (avtomatik)
- ✅ **CDN** (tez yuklash)

**Saytingiz professional va scalable!** 🚀

---

**Qo'shimcha savollar bo'lsa, yozing!** 😊
