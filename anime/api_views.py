from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Movie, Category, Reel, CustomUser, AnimeNews
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    CategorySerializer, 
    ReelSerializer,
    CustomUserSerializer,
    AnimeNewsSerializer,
    StorySerializer
)
from django.utils import timezone
from django.db import models

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all().order_by('-created_at')
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

class HeroMovieListView(generics.ListAPIView):
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Movie.objects.filter(is_home_featured=True).order_by('home_featured_order', '-created_at')[:7]

class StoryListView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__gt=timezone.now()) | models.Q(expires_at__isnull=True)
        ).order_by('-created_at')

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [AllowAny]

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ReelListView(generics.ListAPIView):
    queryset = Reel.objects.all().order_by('-created_at')
    serializer_class = ReelSerializer
    permission_classes = [AllowAny]

class AnimeNewsListView(generics.ListAPIView):
    queryset = AnimeNews.objects.all().order_by('-created_at')
    serializer_class = AnimeNewsSerializer
    permission_classes = [AllowAny]

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
