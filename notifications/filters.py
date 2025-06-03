import django_filters
from .models import Notification


class NotificationFilter(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter(
        help_text='Filter by read status'
    )
    verb = django_filters.ChoiceFilter(
        choices=Notification.VERB_CHOICES,
        help_text='Filter by notification type'
    )
    target_type = django_filters.ChoiceFilter(
        choices=Notification.TARGET_TYPE_CHOICES,
        help_text='Filter by target type'
    )
    actor = django_filters.CharFilter(
        field_name='actor__username',
        lookup_expr='icontains',
        help_text='Filter by actor username'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter notifications created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter notifications created before this date'
    )

    class Meta:
        model = Notification
        fields = ['is_read', 'verb', 'target_type', 'actor', 'created_after', 'created_before']