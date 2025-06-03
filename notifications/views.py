from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Notification, NotificationSettings
from .serializers import (
    NotificationSerializer, NotificationSettingsSerializer,
    NotificationMarkAsReadSerializer, NotificationStatsSerializer
)
from .filters import NotificationFilter


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NotificationFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor', 'recipient')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, pk):
    """Mark a specific notification as read"""
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    notification.mark_as_read()

    return Response(
        NotificationSerializer(notification, context={'request': request}).data
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_as_read(request):
    """Mark all notifications as read"""
    serializer = NotificationMarkAsReadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    notification_ids = serializer.validated_data.get('notification_ids', [])

    if notification_ids:
        # Mark specific notifications as read
        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
    else:
        # Mark all notifications as read
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

    return Response({
        'detail': f'{updated_count} notifications marked as read'
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """Delete a specific notification"""
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    notification.delete()

    return Response(
        {'detail': 'Notification deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_all_notifications(request):
    """Clear all notifications for the user"""
    deleted_count = Notification.objects.filter(
        recipient=request.user
    ).delete()[0]

    return Response({
        'detail': f'{deleted_count} notifications cleared'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics"""
    serializer = NotificationStatsSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_notifications(request):
    """Get only unread notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).select_related('actor')[:10]  # Limit to 10 most recent

    serializer = NotificationSerializer(
        notifications,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return NotificationSettings.get_or_create_for_user(self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_notification(request):
    """Create a test notification (for development)"""
    if not request.user.is_staff:
        return Response(
            {'detail': 'Only staff can create test notifications'},
            status=status.HTTP_403_FORBIDDEN
        )

    notification = Notification.create_notification(
        recipient=request.user,
        actor=request.user,
        verb='liked_post',
        target_type='post',
        target_id=1
    )

    if notification:
        serializer = NotificationSerializer(notification, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(
            {'detail': 'Could not create test notification'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Utility functions for creating notifications
def create_follow_notification(follower, following_user):
    """Create notification when someone follows a user"""
    return Notification.create_notification(
        recipient=following_user,
        actor=follower,
        verb='followed',
        target_type='profile',
        target_id=following_user.profile.id
    )


def create_like_post_notification(liker, post):
    """Create notification when someone likes a post"""
    return Notification.create_notification(
        recipient=post.author,
        actor=liker,
        verb='liked_post',
        target_type='post',
        target_id=post.id
    )


def create_like_comment_notification(liker, comment):
    """Create notification when someone likes a comment"""
    return Notification.create_notification(
        recipient=comment.author,
        actor=liker,
        verb='liked_comment',
        target_type='comment',
        target_id=comment.id
    )


def create_comment_notification(commenter, post):
    """Create notification when someone comments on a post"""
    return Notification.create_notification(
        recipient=post.author,
        actor=commenter,
        verb='commented',
        target_type='post',
        target_id=post.id
    )


def create_reply_notification(replier, comment):
    """Create notification when someone replies to a comment"""
    return Notification.create_notification(
        recipient=comment.author,
        actor=replier,
        verb='replied',
        target_type='comment',
        target_id=comment.id
    )