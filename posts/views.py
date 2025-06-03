from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Post, Like
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    LikeSerializer, PostListSerializer
)
from .filters import PostFilter
from .permissions import IsAuthorOrReadOnly


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.filter(is_active=True).select_related('author')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'title', 'likes_count', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)

        # Return full post data
        response_serializer = PostSerializer(post, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_active=True).select_related('author')
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostUpdateSerializer
        return PostSerializer

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Post deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk, is_active=True)
    content_type = ContentType.objects.get_for_model(Post)

    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=post.id
    )

    if not created:
        return Response(
            {'detail': 'Post already liked'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create notification for post author
    if post.author != request.user:
        from notifications.models import Notification
        Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb='liked_post',
            target_type='post',
            target_id=post.id
        )

    return Response(
        LikeSerializer(like, context={'request': request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_post(request, pk):
    post = get_object_or_404(Post, pk=pk, is_active=True)
    content_type = ContentType.objects.get_for_model(Post)

    try:
        like = Like.objects.get(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        )
        like.delete()

        # Remove notification
        from notifications.models import Notification
        Notification.objects.filter(
            recipient=post.author,
            actor=request.user,
            verb='liked_post',
            target_type='post',
            target_id=post.id
        ).delete()

        return Response(
            {'detail': 'Post unliked successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    except Like.DoesNotExist:
        return Response(
            {'detail': 'Post not liked yet'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserPostsView(generics.ListAPIView):
    """Get posts by specific user"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'title', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        username = self.kwargs['username']
        return Post.objects.filter(
            author__username=username,
            is_active=True
        ).select_related('author')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_posts(request):
    """Get current user's posts"""
    posts = Post.objects.filter(
        author=request.user,
        is_active=True
    ).select_related('author')

    serializer = PostListSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def feed(request):
    """Get posts from followed users"""
    following_users = request.user.following.values_list('following__user', flat=True)
    posts = Post.objects.filter(
        author__in=following_users,
        is_active=True
    ).select_related('author')[:20]
    serializer = PostListSerializer(
        posts,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)