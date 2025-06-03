from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import Follow
from posts.models import Like
from comments.models import Comment
from .models import Notification, NotificationSettings
from django.contrib.contenttypes.models import ContentType


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when someone follows a user"""
    if created:
        Notification.create_notification(
            recipient=instance.following.user,
            actor=instance.follower,
            verb='followed',
            target_type='profile',
            target_id=instance.following.id
        )


@receiver(post_delete, sender=Follow)
def delete_follow_notification(sender, instance, **kwargs):
    """Delete notification when someone unfollows a user"""
    Notification.objects.filter(
        recipient=instance.following.user,
        actor=instance.follower,
        verb='followed',
        target_type='profile',
        target_id=instance.following.id
    ).delete()


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes a post or comment"""
    if created:
        content_type = instance.content_type
        target_object = instance.content_object

        if content_type.model == 'post':
            Notification.create_notification(
                recipient=target_object.author,
                actor=instance.user,
                verb='liked_post',
                target_type='post',
                target_id=target_object.id
            )
        elif content_type.model == 'comment':
            Notification.create_notification(
                recipient=target_object.author,
                actor=instance.user,
                verb='liked_comment',
                target_type='comment',
                target_id=target_object.id
            )


@receiver(post_delete, sender=Like)
def delete_like_notification(sender, instance, **kwargs):
    """Delete notification when someone unlikes a post or comment"""
    content_type = instance.content_type
    if content_type.model == 'post':
        verb = 'liked_post'
        target_type = 'post'
    elif content_type.model == 'comment':
        verb = 'liked_comment'
        target_type = 'comment'
    else:
        return
    Notification.objects.filter(
        actor=instance.user,
        verb=verb,
        target_type=target_type,
        target_id=instance.object_id
    ).delete()


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Create notification when someone comments on a post or replies to a comment"""
    if created:
        if instance.parent:
            Notification.create_notification(
                recipient=instance.parent.author,
                actor=instance.author,
                verb='replied',
                target_type='comment',
                target_id=instance.parent.id
            )
        else:
            Notification.create_notification(
                recipient=instance.post.author,
                actor=instance.author,
                verb='commented',
                target_type='post',
                target_id=instance.post.id
            )


@receiver(post_save, sender='users.User')
def create_notification_settings(sender, instance, created, **kwargs):
    """Create notification settings for new users"""
    if created:
        NotificationSettings.objects.create(user=instance)