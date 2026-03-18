from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Anime(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Anime nomi",
        help_text="Anime nomini kiriting"
    )
    description = models.TextField(
        verbose_name="Qisqacha ta'rifi",
        help_text="Anime haqida qisqacha ma'lumot"
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
    image_url = models.URLField(
        max_length=500,
        default="https://via.placeholder.com/300x400",
        verbose_name="Rasm havolasi",
        help_text="Anime rasmi URL manzili"
    )
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
            raise ValidationError("Video fayl yoki URL manzilidan birini kiriting")
        if self.episode_number < 1:
            raise ValidationError("Qism raqami 1 dan kichik bo'lishi mumkin emas")
