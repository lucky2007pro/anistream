from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse


class Genre(models.Model):
    """Anime janrlari"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Janr nomi")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Tavsif")

    class Meta:
        verbose_name = "Janr"
        verbose_name_plural = "Janrlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Anime(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Davom etmoqda'),
        ('completed', 'Yakunlangan'),
        ('upcoming', 'Tez orada'),
    ]

    TYPE_CHOICES = [
        ('tv', 'TV Serial'),
        ('movie', 'Film'),
        ('ova', 'OVA'),
        ('special', 'Maxsus'),
    ]
    title = models.CharField(
        max_length=200,
        verbose_name="Anime nomi",
        help_text="Anime nomini kiriting"
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(
        verbose_name="Qisqacha ta'rifi",
        help_text="Anime haqida qisqacha ma'lumot"
    )
    genres = models.ManyToManyField(Genre, related_name='animes', verbose_name="Janrlar")
    anime_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='tv',
        verbose_name="Anime turi"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ongoing',
        verbose_name="Holati"
    )
    release_year = models.IntegerField(
        verbose_name="Chiqarilgan yili",
        validators=[MinValueValidator(1960), MaxValueValidator(2030)],
        help_text="1960 dan 2030 gacha"
    )
    rating = models.FloatField(
        default=0.0,
        verbose_name="Reyting",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="0.0 dan 10.0 gacha"
    )
    views_count = models.IntegerField(default=0, verbose_name="Ko'rishlar soni")
    image_url = models.URLField(
        max_length=500,
        default="https://via.placeholder.com/300x400",
        verbose_name="Rasm havolasi",
        help_text="Anime rasmi URL manzili"
    )
    banner_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Banner rasm",
        help_text="Katta banner rasm (ixtiyoriy)"
    )
    trailer_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Trailer video",
        help_text="Trailer URL (ixtiyoriy)"
    )
    studio = models.CharField(max_length=200, blank=True, verbose_name="Studiya")
    age_rating = models.CharField(max_length=10, default='13+', verbose_name="Yosh chegarasi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anime"
        verbose_name_plural = "Animelar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def clean(self):
        if self.rating < 0 or self.rating > 10:
            raise ValidationError("Reyting 0 dan 10 gacha bo'lishi kerak")


class Episode(models.Model):
    anime = models.ForeignKey(
        'Anime',
        on_delete=models.CASCADE,
        related_name='episodes',
        verbose_name="Anime"
    )
    episode_number = models.IntegerField(
        verbose_name="Qism raqami",
        validators=[MinValueValidator(1)],
        help_text="1 dan boshlanadi"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Qism nomi",
        blank=True,
        null=True,
        help_text="Qismning nomi (ixtiyoriy)"
    )
    video_file = models.FileField(
        upload_to='videos/',
        blank=True,
        null=True,
        verbose_name="Videoni kompyuterdan yuklash",
        help_text="Kompyuterdan video yuklash"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Video silkasi (URL)",
        help_text="Tashqi video silkasi"
    )
    telegram_file_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Telegram file_id",
        help_text="Kichik videolar uchun (Bot API)"
    )
    telegram_message_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Telegram message_id",
        help_text="MTProto stream uchun (Kanal/Guruhdagi xabar ID'si)"
    )
    telegram_channel_post_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Telegram post URL",
        help_text="Telegram kanaldagi xabar havolasi"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Qism (Episode)"
        verbose_name_plural = "Qismlar (Episodes)"
        ordering = ['anime', 'episode_number']
        unique_together = [['anime', 'episode_number']]
        indexes = [
            models.Index(fields=['anime', 'episode_number']),
        ]

    def __str__(self):
        return f"{self.anime.title} - {self.episode_number}-qism"

    def clean(self):
        if not self.video_file and not self.video_url and not self.telegram_file_id:
            raise ValidationError("Video fayl, URL yoki Telegram file_id dan birini kiriting")
        if self.episode_number < 1:
            raise ValidationError("Qism raqami 1 dan kichik bo'lishi mumkin emas")

    def get_video_source(self):
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
        return ""


class ShortVideo(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Lavha nomi",
        help_text="Qisqa video/lavha nomi"
    )
    anime = models.ForeignKey(
        'Anime',
        on_delete=models.CASCADE,
        related_name='shorts',
        blank=True,
        null=True,
        verbose_name="Tegishli Anime"
    )
    telegram_file_id = models.CharField(
        max_length=255, 
        verbose_name="Telegram file_id",
        help_text="Bot orqali yuklangan qisqa video ID'si"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lavha (Short)"
        verbose_name_plural = "Lavhalar (Shorts)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """Foydalanuvchi profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Tug'ilgan kun")
    favorites = models.ManyToManyField(Anime, related_name='favorited_by', blank=True)
    watchlist = models.ManyToManyField(Anime, related_name='in_watchlist', blank=True)
    is_premium = models.BooleanField(default=False, verbose_name="Premium")
    premium_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Foydalanuvchi Profili"
        verbose_name_plural = "Foydalanuvchi Profillari"

    def __str__(self):
        return f"{self.user.username} profili"


class WatchHistory(models.Model):
    """Ko'rish tarixi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True)
    watch_progress = models.IntegerField(default=0, help_text="Daqiqalarda")
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ko'rish Tarixi"
        verbose_name_plural = "Ko'rish Tarixi"
        ordering = ['-last_watched']
        unique_together = ['user', 'anime', 'episode']

    def __str__(self):
        return f"{self.user.username} - {self.anime.title}"


class Comment(models.Model):
    """Izohlar"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"

    def likes_count(self):
        return self.likes.count()


class NewsPost(models.Model):
    """Yangiliklar va Blog"""
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(verbose_name="Matn")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_posts')
    image_url = models.URLField(max_length=500, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Vergul bilan ajrating")
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
