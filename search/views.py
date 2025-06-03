from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from posts.models import Post
from comments.models import Comment
from users.models import Profile
from .models import SearchHistory, PopularSearch, SearchSuggestion
from .serializers import (
    SearchResultSerializer, SearchQuerySerializer, SearchHistorySerializer,
    PopularSearchSerializer, SearchSuggestionSerializer, AutocompleteSerializer
)
from .utils import get_client_ip


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search(request):
    """Main search endpoint"""
    serializer = SearchQuerySerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    query = serializer.validated_data['q']
    search_type = serializer.validated_data['type']
    page = serializer.validated_data['page']
    page_size = serializer.validated_data['page_size']
    search_history = SearchHistory.objects.create(
        user=request.user if request.user.is_authenticated else None,
        query=query,
        search_type=search_type,
        ip_address=get_client_ip(request)
    )
    PopularSearch.increment_search(query)
    results = {}
    total_results = 0
    if search_type in ['all', 'post']:
        posts = search_posts(query, page if search_type == 'post' else 1,
                             page_size if search_type == 'post' else 5)
        results['posts'] = posts['results']
        if search_type == 'post':
            total_results = posts['total']

    if search_type in ['all', 'comment']:
        comments = search_comments(query, page if search_type == 'comment' else 1,
                                   page_size if search_type == 'comment' else 5)
        results['comments'] = comments['results']
        if search_type == 'comment':
            total_results = comments['total']

    if search_type in ['all', 'user']:
        users = search_users(query, page if search_type == 'user' else 1,
                             page_size if search_type == 'user' else 5)
        results['users'] = users['results']
        if search_type == 'user':
            total_results = users['total']

    if search_type == 'all':
        total_results = sum([
            results.get('posts', {}).get('total', 0),
            results.get('comments', {}).get('total', 0),
            results.get('users', {}).get('total', 0)
        ])
    search_history.results_count = total_results
    search_history.save(update_fields=['results_count'])
    response_data = {
        'posts': results.get('posts', {}).get('data', []),
        'comments': results.get('comments', {}).get('data', []),
        'users': results.get('users', {}).get('data', []),
        'total_results': total_results,
        'query': query,
        'search_type': search_type
    }
    return Response(response_data)


def search_posts(query, page=1, page_size=10):
    """Search posts using PostgreSQL full-text search"""
    posts_queryset = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        is_active=True
    ).select_related('author').order_by('-created_at')
    try:
        search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
        search_query = SearchQuery(query)
        posts_queryset = Post.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query,
            is_active=True
        ).order_by('-rank', '-created_at')
    except:
        pass
    paginator = Paginator(posts_queryset, page_size)
    posts_page = paginator.get_page(page)
    from posts.serializers import PostListSerializer
    serializer = PostListSerializer(posts_page, many=True)
    return {
        'results': {
            'data': serializer.data,
            'total': paginator.count,
            'page': page,
            'pages': paginator.num_pages
        },
        'total': paginator.count
    }


def search_comments(query, page=1, page_size=10):
    """Search comments"""
    comments_queryset = Comment.objects.filter(
        content__icontains=query,
        is_active=True
    ).select_related('author', 'post').order_by('-created_at')
    paginator = Paginator(comments_queryset, page_size)
    comments_page = paginator.get_page(page)
    from comments.serializers import CommentListSerializer
    serializer = CommentListSerializer(comments_page, many=True)
    return {
        'results': {
            'data': serializer.data,
            'total': paginator.count,
            'page': page,
            'pages': paginator.num_pages
        },
        'total': paginator.count
    }


def search_users(query, page=1, page_size=10):
    """Search users/profiles"""
    profiles_queryset = Profile.objects.filter(
        Q(user__username__icontains=query) |
        Q(user__email__icontains=query) |
        Q(bio__icontains=query)
    ).select_related('user').order_by('user__username')
    paginator = Paginator(profiles_queryset, page_size)
    profiles_page = paginator.get_page(page)
    from users.serializers import ProfileSerializer
    serializer = ProfileSerializer(profiles_page, many=True)
    return {
        'results': {
            'data': serializer.data,
            'total': paginator.count,
            'page': page,
            'pages': paginator.num_pages
        },
        'total': paginator.count
    }


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def autocomplete(request):
    """Autocomplete suggestions for search"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return Response({
            'suggestions': [],
            'popular_searches': [],
            'manual_suggestions': []
        })
    suggestions = []
    post_titles = Post.objects.filter(
        title__icontains=query,
        is_active=True
    ).values_list('title', flat=True)[:5]
    suggestions.extend(post_titles)
    usernames = Profile.objects.filter(
        user__username__icontains=query
    ).values_list('user__username', flat=True)[:5]
    suggestions.extend([f"@{username}" for username in usernames])
    popular_searches = PopularSearch.objects.filter(
        query__icontains=query
    )[:5]
    manual_suggestions = SearchSuggestion.objects.filter(
        suggestion__icontains=query,
        is_active=True
    )[:5]
    response_data = {
        'suggestions': list(set(suggestions))[:10],  # Remove duplicates and limit
        'popular_searches': PopularSearchSerializer(popular_searches, many=True).data,
        'manual_suggestions': SearchSuggestionSerializer(manual_suggestions, many=True).data
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_searches(request):
    """Get trending search terms"""
    week_ago = timezone.now() - timedelta(days=7)
    trending = PopularSearch.objects.filter(
        last_searched__gte=week_ago
    ).order_by('-search_count')[:10]
    serializer = PopularSearchSerializer(trending, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_history(request):
    """Get user's search history"""
    history = SearchHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    serializer = SearchHistorySerializer(history, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_search_history(request):
    """Clear user's search history"""
    deleted_count = SearchHistory.objects.filter(user=request.user).delete()[0]
    return Response({
        'detail': f'{deleted_count} search history entries cleared'
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    """Get manual search suggestions by category"""
    category = request.GET.get('category', 'general')
    suggestions = SearchSuggestion.objects.filter(
        category=category,
        is_active=True
    ).order_by('-priority', 'suggestion')
    serializer = SearchSuggestionSerializer(suggestions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_stats(request):
    """Get search statistics"""
    total_searches = SearchHistory.objects.count()
    unique_queries = SearchHistory.objects.values('query').distinct().count()
    recent_searches = SearchHistory.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    top_queries = PopularSearch.objects.order_by('-search_count')[:5]
    return Response({
        'total_searches': total_searches,
        'unique_queries': unique_queries,
        'recent_searches': recent_searches,
        'top_queries': PopularSearchSerializer(top_queries, many=True).data
    })


class AdvancedSearchView(generics.GenericAPIView):
    """Advanced search with filters"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'detail': 'Search query is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        author = request.GET.get('author')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        content_type = request.GET.get('type', 'all')
        sort_by = request.GET.get('sort', 'relevance')
        results = {}
        if content_type in ['all', 'post']:
            posts_qs = Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                is_active=True
            )
            if author:
                posts_qs = posts_qs.filter(author__username__icontains=author)
            if date_from:
                posts_qs = posts_qs.filter(created_at__gte=date_from)
            if date_to:
                posts_qs = posts_qs.filter(created_at__lte=date_to)
            if sort_by == 'date':
                posts_qs = posts_qs.order_by('-created_at')
            elif sort_by == 'popularity':
                posts_qs = posts_qs.annotate(
                    like_count=Count('likes')
                ).order_by('-like_count')
            from posts.serializers import PostListSerializer
            results['posts'] = PostListSerializer(
                posts_qs[:20], many=True, context={'request': request}
            ).data
        return Response(results)