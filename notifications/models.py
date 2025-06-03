from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Notification(models.Model):
    VERB_CHOICES = [
        ('followed', 'Followed'),
        ('liked_post', 'Liked Post'),
        ('liked_comment', 'Liked Comment'),
        ('commented', 'Commented'),
        ('replied', 'Replied'),
    ]

    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('profile', 'Profile'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_received'
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_sent'
    )
    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    target_type = models.CharField(max_length=10, choices=TARGET_TYPE_CHOICES)
    target_id = models.PositiveIntegerField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['actor']),
            models.Index(fields=['target_type', 'target_id']),
        ]
        unique_together = ['recipient', 'actor', 'verb', 'target_type', 'target_id']

    def __str__(self):
        return f"{self.actor.username} {self.verb} {self.recipient.username}'s {self.target_type}"

    @property
    def target_object(self):
        """Get the actual target object"""
        if self.target_type == 'post':
            from posts.models import Post
            try:
                return Post.objects.get(id=self.target_id)
            except Post.DoesNotExist:
                return None
        elif self.target_type == 'comment':
            from comments.models import Comment
            try:
                return Comment.objects.get(id=self.target_id)
            except Comment.DoesNotExist:
                return None
        elif self.target_type == 'profile':
            from users.models import Profile
            try:
                return Profile.objects.get(id=self.target_id)
            except Profile.DoesNotExist:
                return None
        return None

    @property
    def message(self):
        """Generate human-readable notification message"""
        target_obj = self.target_object
        if self.verb == 'followed':
            return f"{self.actor.username} started following you"
        elif self.verb == 'liked_post' and target_obj:
            return f"{self.actor.username} liked your post '{target_obj.title[:30]}...'"
        elif self.verb == 'liked_comment' and target_obj:
            return f"{self.actor.username} liked your comment"
        elif self.verb == 'commented' and target_obj:
            return f"{self.actor.username} commented on your post '{target_obj.title[:30]}...'"
        elif self.verb == 'replied' and target_obj:
            return f"{self.actor.username} replied to your comment"

        return f"{self.actor.username} {self.verb}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @classmethod
    def create_notification(cls, recipient, actor, verb, target_type, target_id):
        """Create notification with duplicate prevention"""
        if recipient == actor:
            return None  # Don't notify yourself
        recent_notification = cls.objects.filter(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target_type=target_type,
            target_id=target_id,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).first()
        if recent_notification:
            recent_notification.created_at = timezone.now()
            recent_notification.is_read = False
            recent_notification.save()
            return recent_notification
        try:
            notification = cls.objects.create(
                recipient=recipient,
                actor=actor,
                verb=verb,
                target_type=target_type,
                target_id=target_id
            )
            return notification
        except Exception:
            return None


class NotificationSettings(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    email_notifications = models.BooleanField(default=True)
    follow_notifications = models.BooleanField(default=True)
    like_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    reply_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s notification settings"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create notification settings for user"""
        settings, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'email_notifications': True,
                'follow_notifications': True,
                'like_notifications': True,
                'comment_notifications': True,
                'reply_notifications': True,
            }
        )
        return settings