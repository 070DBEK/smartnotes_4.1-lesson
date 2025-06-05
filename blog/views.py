from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment, Like, Notification
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    LikeSerializer, NotificationSerializer
)
from accounts.models import Profile
from accounts.serializers import ProfileSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title', 'likes_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostUpdateSerializer
        return PostSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user and request.user.role != 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user and request.user.role != 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        post.is_active = False
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, id):
    post = get_object_or_404(Post, id=id, is_active=True)
    content_type = ContentType.objects.get_for_model(Post)

    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=post.id
    )

    if not created:
        return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)

    # Create notification
    if post.author != request.user:
        Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            verb='liked_post',
            target_type='post',
            target_id=post.id
        )

    return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_post(request, id):
    post = get_object_or_404(Post, id=id, is_active=True)
    content_type = ContentType.objects.get_for_model(Post)

    try:
        like = Like.objects.get(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        )
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        return Response({'detail': 'Not liked yet'}, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, is_active=True)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id, is_active=True)
        comment = serializer.save(author=self.request.user, post=post)

        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=self.request.user,
                verb='commented',
                target_type='post',
                target_id=post.id
            )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user and request.user.role != 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user and request.user.role != 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        comment.is_active = False
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_comment(request, id):
    comment = get_object_or_404(Comment, id=id, is_active=True)
    content_type = ContentType.objects.get_for_model(Comment)

    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=comment.id
    )

    if not created:
        return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)

    if comment.author != request.user:
        Notification.objects.create(
            recipient=comment.author,
            actor=request.user,
            verb='liked_comment',
            target_type='comment',
            target_id=comment.id
        )

    return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_comment(request, id):
    comment = get_object_or_404(Comment, id=id, is_active=True)
    content_type = ContentType.objects.get_for_model(Comment)

    try:
        like = Like.objects.get(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        )
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        return Response({'detail': 'Not liked yet'}, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, id):
    notification = get_object_or_404(Notification, id=id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return Response(NotificationSerializer(notification).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'detail': 'All notifications marked as read'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    if not query:
        return Response({'detail': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    results = {}

    if search_type in ['post', 'all']:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        )
        results['posts'] = {
            'count': posts.count(),
            'results': PostSerializer(posts[:10], many=True).data
        }

    if search_type in ['comment', 'all']:
        comments = Comment.objects.filter(
            content__icontains=query,
            is_active=True
        )
        results['comments'] = {
            'count': comments.count(),
            'results': CommentSerializer(comments[:10], many=True).data
        }

    if search_type in ['user', 'all']:
        profiles = Profile.objects.filter(
            Q(user__username__icontains=query) | Q(bio__icontains=query)
        )
        results['users'] = {
            'count': profiles.count(),
            'results': ProfileSerializer(profiles[:10], many=True).data
        }

    return Response(results)
