# 🚀 Deployment Instructions - AniStream

## ✅ Tekshirish (Pre-deployment Checklist)

Render.com ga deploy qilishdan oldin quyidagilarni tekshiring:

### 1. Virtual environment'da dependencies o'rnating

```bash
# Virtual environment yarating va aktivlashtiring
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Dependencies o'rnating
pip install -r requirements.txt
```

### 2. Migrations yarating va ishga tushiring

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Static files to'plang

```bash
python manage.py collectstatic --no-input
```

### 4. Superuser yarating (local test uchun)

```bash
python manage.py createsuperuser
```

### 5. Local serverni test qiling

```bash
python manage.py runserver
```

Sahifa `http://127.0.0.1:8000/` da ochilishi kerak.

---

## 🌐 Render.com'ga Deploy qilish

### Step 1: GitHub Repository yarating

1. GitHub'da yangi repository yarating
2. Local kodni push qiling:

```bash
git init
git add .
git commit -m "Initial commit: AniStream ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AniDev.git
git push -u origin main
```

### Step 2: Render.com'da Web Service yarating

1. [render.com](https://render.com) ga kiring
2. **Dashboard** > **New** > **Web Service** ni tanlang
3. GitHub repository'ni ulang
4. Quyidagi sozlamalarni kiriting:

**Asosiy sozlamalar:**
- **Name**: `anistream` (yoki istalgan nom)
- **Region**: Yaqin region tanlang (Frankfurt, Singapore, etc.)
- **Branch**: `main`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```bash
  ./build.sh
  ```
- **Start Command**: 
  ```bash
  gunicorn core.wsgi:application
  ```

**Instance Type:**
- **Free** (bepul tier)

### Step 3: Environment Variables qo'shing

**Environment** bo'limida quyidagi o'zgaruvchilarni qo'shing:

```env
SECRET_KEY=your-super-secret-key-here-change-this-now-123456789
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
PYTHON_VERSION=3.12.0
```

**SECRET_KEY generatsiya qilish:**

Python terminalda:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 4: PostgreSQL Database yarating

1. **Dashboard** > **New** > **PostgreSQL** ni tanlang
2. Database sozlamalari:
   - **Name**: `anistream-db`
   - **Region**: Web Service bilan bir xil
   - **PostgreSQL Version**: 16
   - **Instance Type**: Free

3. Database yaratilgandan keyin:
   - **Internal Database URL** ni nusxalang
   - Web Service'ning **Environment** bo'limida `DATABASE_URL` qo'shing

### Step 5: Deploy qiling!

1. **Manual Deploy** > **Deploy latest commit** tugmasini bosing
2. Build jarayonini kuzating (5-10 daqiqa)
3. Deploy tugagach, linkni oching: `https://your-app-name.onrender.com`

---

## 🔧 Deploy Keyin Qilinadigan Ishlar

### 1. Admin Panel uchun Superuser yarating

Render Dashboard'da **Shell** tugmasini bosing va:

```bash
python manage.py createsuperuser
```

### 2. Domen sozlash (Custom Domain)

1. Render'da **Settings** > **Custom Domain**
2. O'z domeningizni qo'shing
3. DNS sozlamalarni yangilang

### 3. SSL Certificate

Render avtomatik ravishda Let's Encrypt SSL sertifikatini qo'shadi. ✅

---

## 🐛 Muammolarni Hal Qilish

### Build muvaffaqiyatsiz bo'lsa:

1. **Logs**'ni tekshiring
2. `requirements.txt` to'g'riligini tekshiring
3. `build.sh` execute ruxsatini tekshiring:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

### Database bilan bog'lanish muammolari:

1. `DATABASE_URL` to'g'ri sozlanganligini tekshiring
2. PostgreSQL database ishlab turganligini tekshiring
3. Migrations ishga tushganligini logs'dan tekshiring

### Static files ko'rinmayapti:

1. `STATIC_ROOT` va `STATIC_URL` sozlamalarni tekshiring
2. `collectstatic` buyrug'i ishlashini tekshiring
3. `whitenoise` middleware to'g'ri joylashganligini tekshiring

### 500 Internal Server Error:

1. `DEBUG=False` bo'lishi kerak
2. `ALLOWED_HOSTS` to'g'ri sozlanganligini tekshiring
3. Logs'ni diqqat bilan o'qing:
   - Render Dashboard > Logs

---

## 📊 Performance Monitoring

### Render Metrics

Render Dashboard'da:
- **Metrics** > CPU, Memory, Response time
- **Logs** > Real-time application logs

### Database Monitoring

PostgreSQL Dashboard'da:
- Connection count
- Query performance
- Storage usage

---

## 🔄 Yangilanishlar (Updates)

Kod o'zgartirgandan keyin:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Render avtomatik ravishda yangi deploy qiladi (Auto-Deploy yoqilgan bo'lsa).

---

## 💰 Free Tier Cheklovlari

Render Free tier:
- ✅ 750 soat/oy
- ✅ Avtomatik SSL
- ✅ PostgreSQL database (90 kun)
- ⚠️ 15 daqiqa faollik yo'qligida sleep mode
- ⚠️ Monthly restart (bepul tier uchun)

---

## 🎯 Production Best Practices

1. ✅ Environment variables (.env) ni `.gitignore`ga qo'shing
2. ✅ `DEBUG=False` production'da
3. ✅ Kuchli `SECRET_KEY` ishlatíng
4. ✅ Database backup qiling muntazam ravishda
5. ✅ HTTPS majburiy qiling (Render avtomatik qiladi)
6. ✅ Error monitoring qo'shing (Sentry, Rollbar)
7. ✅ Regular security updates

---

## 📞 Yordam

Muammo bo'lsa:
- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- GitHub Issues: Create an issue in repository

---

**Muvaffaqiyat tilayman! 🚀**
