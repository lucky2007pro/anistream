from rest_framework import serializers
from .models import Movie, Category, MovieEpisode, Reel, CustomUser, AnimeNews, Story

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class MovieEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieEpisode
        fields = ['id', 'episode_number', 'title', 'video_url', 'video_file', 'description']

class MovieListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'image', 'is_premium', 'minimum_tier', 'category_name', 'views_count']

class MovieDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    episodes = MovieEpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'

class ReelSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    video_src = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = ['id', 'user_name', 'title', 'description', 'video_src', 'thumbnail', 'views_count', 'shares_count', 'created_at']

    def get_video_src(self, obj):
        return obj.get_video_src()

class CustomUserSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source='active_tier', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'tier', 'avatar']

class AnimeNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimeNews
        fields = '__all__'

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'image', 'video', 'link_url', 'expires_at', 'created_at']
