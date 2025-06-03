from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'post_title', 'content_preview', 'parent',
        'created_at', 'is_active', 'likes_count', 'replies_count'
    )
    list_filter = ('is_active', 'created_at', 'parent')
    search_fields = ('content', 'author__username', 'author__email', 'post__title')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'replies_count')
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Comment Information', {
            'fields': ('content', 'author', 'post', 'parent')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('likes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post', 'parent')

    def post_title(self, obj):
        return obj.post.title[:50] + "..." if len(obj.post.title) > 50 else obj.post.title

    post_title.short_description = 'Post'

    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = 'Content Preview'

    def has_delete_permission(self, request, obj=None):
        # Only allow soft delete through the admin
        return False

    def delete_model(self, request, obj):
        # Soft delete
        obj.is_active = False
        obj.save()

    def delete_queryset(self, request, queryset):
        # Soft delete for bulk operations
        queryset.update(is_active=False)