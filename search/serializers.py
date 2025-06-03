from rest_framework import serializers
from .models import SearchHistory, PopularSearch, SearchSuggestion
from posts.serializers import PostListSerializer
from comments.serializers import CommentListSerializer
from users.serializers import ProfileSerializer


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'search_type', 'results_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class PopularSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularSearch
        fields = ['query', 'search_count', 'last_searched']


class SearchSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchSuggestion
        fields = ['suggestion', 'category', 'priority']


class SearchResultSerializer(serializers.Serializer):
    """Combined search results serializer"""
    posts = PostListSerializer(many=True, read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)
    users = ProfileSerializer(many=True, read_only=True)
    total_results = serializers.IntegerField(read_only=True)
    query = serializers.CharField(read_only=True)
    search_type = serializers.CharField(read_only=True)


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for search query validation"""
    q = serializers.CharField(
        min_length=1,
        max_length=255,
        help_text="Search query"
    )
    type = serializers.ChoiceField(
        choices=['all', 'post', 'comment', 'user'],
        default='all',
        help_text="Type of content to search"
    )
    page = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="Page number"
    )
    page_size = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=100,
        help_text="Number of results per page"
    )

    def validate_q(self, value):
        """Validate and clean search query"""
        query = value.strip()
        if len(query) < 1:
            raise serializers.ValidationError("Search query cannot be empty.")
        return query


class AutocompleteSerializer(serializers.Serializer):
    """Serializer for autocomplete suggestions"""
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    popular_searches = PopularSearchSerializer(many=True, read_only=True)
    manual_suggestions = SearchSuggestionSerializer(many=True, read_only=True)