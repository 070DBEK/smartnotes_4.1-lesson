from rest_framework import serializers
from .models import Notification, NotificationSettings
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    message = serializers.ReadOnlyField()
    target_object = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'verb', 'target_type', 'target_id',
            'is_read', 'created_at', 'message', 'target_object', 'time_since'
        ]
        read_only_fields = ['id', 'actor', 'verb', 'target_type', 'target_id', 'created_at']

    def get_target_object(self, obj):
        """Get basic info about target object"""
        target = obj.target_object
        if not target:
            return None

        if obj.target_type == 'post':
            return {
                'id': target.id,
                'title': target.title,
                'type': 'post'
            }
        elif obj.target_type == 'comment':
            return {
                'id': target.id,
                'content': target.content[:100] + "..." if len(target.content) > 100 else target.content,
                'post_title': target.post.title,
                'type': 'comment'
            }
        elif obj.target_type == 'profile':
            return {
                'id': target.id,
                'username': target.user.username,
                'type': 'profile'
            }
        return None

    def get_time_since(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        else:
            return obj.created_at.strftime("%b %d")


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = [
            'email_notifications', 'follow_notifications', 'like_notifications',
            'comment_notifications', 'reply_notifications'
        ]


class NotificationMarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs to mark as read. If empty, marks all as read."
    )


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    recent_count = serializers.IntegerField()

    def to_representation(self, instance):
        # instance should be the user
        notifications = Notification.objects.filter(recipient=instance)

        return {
            'total_count': notifications.count(),
            'unread_count': notifications.filter(is_read=False).count(),
            'recent_count': notifications.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }