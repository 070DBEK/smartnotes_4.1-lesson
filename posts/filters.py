import django_filters
from django.contrib.auth import get_user_model
from .models import Post


User = get_user_model()


class PostFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains',
        help_text='Filter by author username'
    )
    author_id = django_filters.NumberFilter(
        field_name='author__id',
        help_text='Filter by author ID'
    )
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter by title containing text'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter posts created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter posts created before this date'
    )

    class Meta:
        model = Post
        fields = ['author', 'author_id', 'title', 'created_after', 'created_before']