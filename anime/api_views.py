from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Movie, Category, Reel, CustomUser, AnimeNews
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    CategorySerializer, 
    ReelSerializer,
    CustomUserSerializer,
    AnimeNewsSerializer
)

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all().order_by('-created_at')
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

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
