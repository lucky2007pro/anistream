from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Movie, Category, Reel, CustomUser, AnimeNews, FavoriteAnime, WatchHistory, ReelComment, ReelLike
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    CategorySerializer, 
    ReelSerializer,
    CustomUserSerializer,
    AnimeNewsSerializer,
    StorySerializer,
    FavoriteAnimeSerializer,
    WatchHistorySerializer,
    ReelCommentSerializer
)
from django.utils import timezone
from django.db import models
from django.db.models import F
from django.shortcuts import get_object_or_404

class MovieListView(generics.ListAPIView):
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Movie.objects.all().order_by('-created_at')
        search_query = self.request.query_params.get('search', None)
        category_id = self.request.query_params.get('category', None)
        
        if search_query:
            queryset = queryset.filter(models.Q(title__icontains=search_query) | models.Q(description__icontains=search_query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset

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

    def get_object(self):
        obj = super().get_object()
        Movie.objects.filter(id=obj.id).update(views_count=F('views_count') + 1)
        obj.refresh_from_db()
        
        if self.request.user.is_authenticated:
            WatchHistory.objects.update_or_create(
                user=self.request.user, movie=obj, 
                defaults={'last_watched': timezone.now()}
            )
        return obj

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

class WatchHistoryListView(generics.ListAPIView):
    serializer_class = WatchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WatchHistory.objects.filter(user=self.request.user).order_by('-last_watched')

class FavoriteAnimeListView(generics.ListAPIView):
    serializer_class = FavoriteAnimeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteAnime.objects.filter(user=self.request.user).order_by('-created_at')

class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        movie = get_object_or_404(Movie, id=pk)
        fav, created = FavoriteAnime.objects.get_or_create(user=request.user, movie=movie)
        if not created:
            fav.delete()
            is_favorited = False
        else:
            is_favorited = True
        return Response({'is_favorited': is_favorited})

class ToggleReelLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        reel = get_object_or_404(Reel, id=pk)
        like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response({
            'liked': liked,
            'total_likes': reel.likes.count(),
        })

class AddReelCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        reel = get_object_or_404(Reel, id=pk)
        text = request.data.get('text', '').strip()
        reply_to_id = request.data.get('reply_to')

        if not text:
            return Response({'error': "Izoh bo'sh bo'lmasin"}, status=400)

        reply_obj = None
        if reply_to_id:
            try:
                reply_obj = ReelComment.objects.get(id=int(reply_to_id))
            except (ReelComment.DoesNotExist, ValueError):
                pass

        comment = ReelComment.objects.create(
            reel=reel,
            user=request.user,
            text=text,
            reply_to=reply_obj
        )

        serializer = ReelCommentSerializer(comment)
        return Response(serializer.data, status=201)

class ReelCommentListView(generics.ListAPIView):
    serializer_class = ReelCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        reel_id = self.kwargs['pk']
        return ReelComment.objects.filter(reel_id=reel_id).order_by('-created_at')
