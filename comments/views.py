from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Comment
from posts.models import Post, Like
from .serializers import (
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    CommentListSerializer
)
from .filters import CommentFilter
from .permissions import IsAuthorOrReadOnly


class CommentListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CommentFilter
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(
            post_id=post_id,
            is_active=True,
            parent=None  # Only top-level comments
        ).select_related('author', 'post')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id, is_active=True)
        comment = serializer.save(author=self.request.user, post=post)

        # Create notification for post author (if not commenting on own post)
        if post.author != self.request.user:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=post.author,
                actor=self.request.user,
                verb='commented',
                target_type='post',
                target_id=post.id
            )

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        get_object_or_404(Post, id=post_id, is_active=True)

        serializer = self.get_serializer(
            data=request.data,
            context={'post_id': post_id, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user, post_id=post_id)

        # Return full comment data
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_active=True).select_related('author', 'post')
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CommentUpdateSerializer
        return CommentSerializer

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

        # Also soft delete all replies
        instance.replies.update(is_active=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Comment deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, is_active=True)
    content_type = ContentType.objects.get_for_model(Comment)

    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=comment.id
    )

    if not created:
        return Response(
            {'detail': 'Comment already liked'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create notification for comment author
    if comment.author != request.user:
        from notifications.models import Notification
        Notification.objects.create(
            recipient=comment.author,
            actor=request.user,
            verb='liked_comment',
            target_type='comment',
            target_id=comment.id
        )

    return Response(
        {'detail': 'Comment liked successfully', 'likes_count': comment.likes_count},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlike_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, is_active=True)
    content_type = ContentType.objects.get_for_model(Comment)

    try:
        like = Like.objects.get(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        )
        like.delete()

        # Remove notification
        from notifications.models import Notification
        Notification.objects.filter(
            recipient=comment.author,
            actor=request.user,
            verb='liked_comment',
            target_type='comment',
            target_id=comment.id
        ).delete()

        return Response(
            {'detail': 'Comment unliked successfully', 'likes_count': comment.likes_count},
            status=status.HTTP_204_NO_CONTENT
        )
    except Like.DoesNotExist:
        return Response(
            {'detail': 'Comment not liked yet'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def comment_replies(request, pk):
    """Get all replies for a specific comment"""
    comment = get_object_or_404(Comment, pk=pk, is_active=True)
    replies = comment.get_replies()

    serializer = CommentListSerializer(
        replies,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_comments(request):
    """Get current user's comments"""
    comments = Comment.objects.filter(
        author=request.user,
        is_active=True
    ).select_related('author', 'post')

    serializer = CommentListSerializer(
        comments,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


class UserCommentsView(generics.ListAPIView):
    """Get comments by specific user"""
    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        username = self.kwargs['username']
        return Comment.objects.filter(
            author__username=username,
            is_active=True
        ).select_related('author', 'post')