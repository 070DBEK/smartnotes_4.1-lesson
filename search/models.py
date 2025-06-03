from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.indexes import GinIndex


User = get_user_model()


class SearchHistory(models.Model):
    """Store user search history for analytics and suggestions"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_history',
        null=True,
        blank=True
    )
    query = models.CharField(max_length=255)
    search_type = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All'),
            ('post', 'Posts'),
            ('comment', 'Comments'),
            ('user', 'Users'),
        ],
        default='all'
    )
    results_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query']),
            models.Index(fields=['search_type']),
        ]

    def __str__(self):
        return f"Search: '{self.query}' by {self.user or 'Anonymous'}"


class PopularSearch(models.Model):
    """Track popular search terms"""
    query = models.CharField(max_length=255, unique=True)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-search_count', '-last_searched']
        indexes = [
            models.Index(fields=['-search_count']),
            models.Index(fields=['query']),
        ]

    def __str__(self):
        return f"'{self.query}' ({self.search_count} searches)"

    @classmethod
    def increment_search(cls, query):
        """Increment search count for a query"""
        if len(query.strip()) < 2:
            return None

        query = query.strip().lower()
        popular_search, created = cls.objects.get_or_create(
            query=query,
            defaults={'search_count': 1}
        )

        if not created:
            popular_search.search_count += 1
            popular_search.save(update_fields=['search_count', 'last_searched'])

        return popular_search


class SearchSuggestion(models.Model):
    """Manual search suggestions for better UX"""
    suggestion = models.CharField(max_length=255, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General'),
            ('topic', 'Topic'),
            ('tag', 'Tag'),
            ('user', 'User'),
        ],
        default='general'
    )
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', 'suggestion']
        indexes = [
            models.Index(fields=['is_active', '-priority']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.suggestion