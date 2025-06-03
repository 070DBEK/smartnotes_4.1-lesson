from django.contrib import admin
from .models import SearchHistory, PopularSearch, SearchSuggestion


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('query', 'user', 'search_type', 'results_count', 'created_at', 'ip_address')
    list_filter = ('search_type', 'created_at', 'results_count')
    search_fields = ('query', 'user__username', 'user__email', 'ip_address')
    readonly_fields = ('created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Search Details', {
            'fields': ('query', 'search_type', 'results_count')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_count', 'last_searched', 'created_at')
    list_filter = ('search_count', 'last_searched', 'created_at')
    search_fields = ('query',)
    readonly_fields = ('created_at', 'last_searched')
    ordering = ('-search_count', '-last_searched')
    fieldsets = (
        ('Search Information', {
            'fields': ('query', 'search_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_searched'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ('suggestion', 'category', 'priority', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'priority', 'created_at')
    search_fields = ('suggestion',)
    list_editable = ('priority', 'is_active')
    ordering = ('-priority', 'suggestion')
    fieldsets = (
        ('Suggestion Details', {
            'fields': ('suggestion', 'category', 'priority', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_suggestions', 'deactivate_suggestions']

    def activate_suggestions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} suggestions activated.')
    activate_suggestions.short_description = 'Activate selected suggestions'

    def deactivate_suggestions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} suggestions deactivated.')
    deactivate_suggestions.short_description = 'Deactivate selected suggestions'