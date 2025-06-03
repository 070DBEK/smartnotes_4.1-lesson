from django.urls import path
from . import views


urlpatterns = [
    path('search/', views.search, name='search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='advanced-search'),
    path('search/autocomplete/', views.autocomplete, name='search-autocomplete'),
    path('search/suggestions/', views.search_suggestions, name='search-suggestions'),
    path('search/trending/', views.trending_searches, name='trending-searches'),
    path('search/history/', views.search_history, name='search-history'),
    path('search/history/clear/', views.clear_search_history, name='clear-search-history'),
    path('search/stats/', views.search_stats, name='search-stats'),
]