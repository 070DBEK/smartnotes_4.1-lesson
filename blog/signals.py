from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Notification
from accounts.models import Follow


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.following.user,
            actor=instance.follower,
            verb='followed',
            target_type='profile',
            target_id=instance.following.id
        )
