from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

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
    image = models.ImageField(
        upload_to='anime/images/',
        verbose_name="Rasm",
        help_text="Anime rasmi yuklang",
        blank=True, null=True
    )
    banner = models.ImageField(
        upload_to='anime/banners/',
        blank=True,
        null=True,
        verbose_name="Banner rasm",
        help_text="Katta banner rasm (ixtiyoriy)"
    )
    trailer = models.FileField(
        upload_to='anime/trailers/',
        blank=True,
        null=True,
        verbose_name="Trailer video",
        help_text="Trailer fayli (ixtiyoriy)"
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
        if not self.video_file and not self.video_url:
            raise ValidationError("Video fayl yoki URL dan birini kiriting")
        if self.episode_number < 1:
            raise ValidationError("Qism raqami 1 dan kichik bo'lishi mumkin emas")

    def get_video_source(self):
        if self.video_file:
            return reverse('episode_stream', args=[self.id])
        if self.video_url:
            return self.video_url
        return ""

class Reel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reels', null=True, blank=True)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='reels', null=True, blank=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='reels/videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()

    def get_video_src(self):
        if self.video_file:
            return self.video_file.url
        return self.video_url or ''

    def __str__(self):
        return f"Reel #{self.id} - {self.title or 'No title'}"

class ReelLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reel_likes')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reel')

class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reel_comments')
    text = models.TextField()
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class ReelShare(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)

class Story(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    video = models.FileField(upload_to='stories/videos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def __str__(self):
        return self.title

class StoryView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )

    def can_delete(self, current_user):
        return self.user == current_user or current_user.is_superuser

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"

class SiteSettings(models.Model):
    background_video = models.FileField(
        upload_to='backgrounds/',
        blank=True,
        null=True
    )
    background_image = models.ImageField(
        upload_to='backgrounds/',
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Sayt Sozlamalari"

class UserSettings(models.Model):
    THEME_CHOICES = [
        ('dark', 'Qorong''i'),
        ('white', 'Oq'),
        ('rose', 'Qizil / Ro''za'),
        ('premium', 'Premium (To''q binafsha)'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='dark'
    )
    bg_color = models.CharField(max_length=30, default='#0a0a0f')
    tabbar_on = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - sozlamalar"

class ActiveSession(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Mobil'),
        ('tablet', 'Planshet'),
        ('desktop', 'Kompyuter'),
        ('unknown', 'Noma''lum'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES, default='unknown')
    device_name = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    """Foydalanuvchi profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
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
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
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
