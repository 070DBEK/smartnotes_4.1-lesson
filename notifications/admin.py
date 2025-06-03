from django.contrib import admin
from .models import Notification, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'recipient', 'actor', 'verb', 'target_type',
        'target_id', 'is_read', 'created_at'
    )
    list_filter = ('verb', 'target_type', 'is_read', 'created_at')
    search_fields = (
        'recipient__username', 'recipient__email',
        'actor__username', 'actor__email'
    )
    readonly_fields = ('created_at', 'message')
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'actor', 'verb', 'target_type', 'target_id')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
        ('Generated Message', {
            'fields': ('message',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'actor')

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')

    mark_as_read.short_description = 'Mark selected notifications as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')

    mark_as_unread.short_description = 'Mark selected notifications as unread'


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'email_notifications', 'follow_notifications',
        'like_notifications', 'comment_notifications', 'reply_notifications'
    )
    list_filter = (
        'email_notifications', 'follow_notifications', 'like_notifications',
        'comment_notifications', 'reply_notifications'
    )
    search_fields = ('user__username', 'user__email')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Preferences', {
            'fields': (
                'email_notifications', 'follow_notifications', 'like_notifications',
                'comment_notifications', 'reply_notifications'
            )
        }),
    )