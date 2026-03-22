from django import forms
from django.utils.text import slugify

from .models import Genre, Anime, Episode, NewsPost


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ["name", "slug", "description"]

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name") or ""
        if not slug and name:
            slug = slugify(name)
        return slug


class AnimeForm(forms.ModelForm):
    class Meta:
        model = Anime
        fields = [
            "title",
            "description",
            "genres",
            "anime_type",
            "status",
            "release_year",
            "rating",
            "image_url",
            "banner_url",
            "trailer_url",
            "studio",
            "age_rating",
        ]
        widgets = {
            "genres": forms.CheckboxSelectMultiple,
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class EpisodeForm(forms.ModelForm):
    upload_to_telegram = forms.BooleanField(
        required=False,
        label="Saqlashdan keyin Telegram kanalga yuklash"
    )

    class Meta:
        model = Episode
        fields = [
            "anime",
            "episode_number",
            "title",
            "video_file",
            "video_url",
            "telegram_file_id",
            "telegram_channel_post_url",
        ]

    def clean(self):
        cleaned_data = super().clean()
        video_file = cleaned_data.get("video_file")
        video_url = cleaned_data.get("video_url")

        if not video_file and not video_url:
            telegram_file_id = cleaned_data.get("telegram_file_id")
            if not telegram_file_id:
                raise forms.ValidationError(
                    "Kamida bitta maydonni to'ldiring: video fayl, video URL yoki Telegram file_id."
                )

        if cleaned_data.get("upload_to_telegram") and not video_file:
            raise forms.ValidationError("Telegram'ga yuklash uchun video fayl tanlang.")

        return cleaned_data


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ["title", "slug", "content", "image_url", "tags", "is_published"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        title = self.cleaned_data.get("title") or ""
        if not slug and title:
            slug = slugify(title)
        return slug

