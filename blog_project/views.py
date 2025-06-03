from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

@csrf_exempt
def handler404(request, exception):
    """Custom 404 error handler"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404,
        'path': request.path
    }, status=404)

@csrf_exempt
def handler500(request):
    """Custom 500 error handler"""
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred.',
        'status_code': 500
    }, status=500)

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Blog API is running',
        'debug': settings.DEBUG,
        'version': '1.0.0'
    })

@require_http_methods(["GET"])
def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'name': 'Blog API',
        'version': '1.0.0',
        'description': 'API for a blog/forum application',
        'endpoints': {
            'authentication': {
                'register': '/api/v1/auth/register/',
                'login': '/api/v1/auth/login/',
                'logout': '/api/v1/auth/logout/',
                'refresh': '/api/v1/auth/token/refresh/',
                'verify_email': '/api/v1/auth/verify-email/',
                'password_reset': '/api/v1/auth/password-reset/',
            },
            'users': {
                'current_user': '/api/v1/auth/me/',
                'profiles': '/api/v1/auth/profiles/{username}/',
                'follow': '/api/v1/auth/profiles/{username}/follow/',
                'unfollow': '/api/v1/auth/profiles/{username}/unfollow/',
            },
            'posts': {
                'list_create': '/api/v1/posts/',
                'detail': '/api/v1/posts/{id}/',
                'like': '/api/v1/posts/{id}/like/',
                'unlike': '/api/v1/posts/{id}/unlike/',
                'user_posts': '/api/v1/users/{username}/posts/',
                'my_posts': '/api/v1/my-posts/',
                'feed': '/api/v1/feed/',
            },
            'comments': {
                'post_comments': '/api/v1/posts/{post_id}/comments/',
                'detail': '/api/v1/comments/{id}/',
                'like': '/api/v1/comments/{id}/like/',
                'unlike': '/api/v1/comments/{id}/unlike/',
                'replies': '/api/v1/comments/{id}/replies/',
            },
            'notifications': {
                'list': '/api/v1/notifications/',
                'mark_read': '/api/v1/notifications/{id}/mark-as-read/',
                'mark_all_read': '/api/v1/notifications/mark-all-read/',
                'stats': '/api/v1/notifications/stats/',
                'settings': '/api/v1/notification-settings/',
            },
            'search': {
                'search': '/api/v1/search/',
                'autocomplete': '/api/v1/search/autocomplete/',
                'trending': '/api/v1/search/trending/',
                'history': '/api/v1/search/history/',
            }
        },
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
        }
    })