import django_filters
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

class CommentFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='icontains',
        help_text='Filter by author username'
    )
    author_id = django_filters.NumberFilter(
        field_name='author__id',
        help_text='Filter by author ID'
    )
    content = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        help_text='Filter by content containing text'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter comments created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter comments created before this date'
    )
    has_replies = django_filters.BooleanFilter(
        method='filter_has_replies',
        help_text='Filter comments that have replies'
    )

    class Meta:
        model = Comment
        fields = ['author', 'author_id', 'content', 'created_after', 'created_before', 'has_replies']

    def filter_has_replies(self, queryset, name, value):
        if value:
            return queryset.filter(replies__isnull=False).distinct()
        else:
            return queryset.filter(replies__isnull=True)