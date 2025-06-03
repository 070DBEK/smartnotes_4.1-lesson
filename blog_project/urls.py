"""
URL configuration for blog_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="API for a blog/forum application with user authentication, posts, comments, likes, and notifications",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@blogapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Welcome to Blog API',
        'version': 'v1',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'posts': '/api/v1/posts/',
            'comments': '/api/v1/comments/',
            'notifications': '/api/v1/notifications/',
            'search': '/api/v1/search/',
            'admin': '/admin/',
            'docs': '/swagger/',
            'redoc': '/redoc/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root, name='api-root'),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/', include('posts.urls')),
    path('api/v1/', include('comments.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('search.urls')),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = 'blog_project.views.handler404'
handler500 = 'blog_project.views.handler500'


admin.site.site_header = "Blog API Administration"
admin.site.site_title = "Blog API Admin Portal"
admin.site.index_title = "Welcome to Blog API Administration"