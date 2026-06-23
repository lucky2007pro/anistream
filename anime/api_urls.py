from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('movies/', api_views.MovieListView.as_view(), name='api_movies'),
    path('hero-movies/', api_views.HeroMovieListView.as_view(), name='api_hero_movies'),
    path('stories/', api_views.StoryListView.as_view(), name='api_stories'),
    path('movies/<int:pk>/', api_views.MovieDetailView.as_view(), name='api_movie_detail'),
    path('categories/', api_views.CategoryListView.as_view(), name='api_categories'),
    path('reels/', api_views.ReelListView.as_view(), name='api_reels'),
    path('news/', api_views.AnimeNewsListView.as_view(), name='api_news'),
    path('user/', api_views.CurrentUserView.as_view(), name='api_current_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
