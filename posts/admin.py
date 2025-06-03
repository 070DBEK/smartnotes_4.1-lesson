from django.contrib import admin
from .models import Post, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'is_active', 'likes_count', 'comments_count')
    list_filter = ('is_active', 'created_at', 'updated_at', 'author')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count')
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'content', 'author')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'content_object', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')