from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from posts.models import Post


User = get_user_model()


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['post']),
            models.Index(fields=['author']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def replies_count(self):
        return self.replies.filter(is_active=True).count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False

    def get_replies(self):
        return self.replies.filter(is_active=True).order_by('created_at')


from posts.models import Like
Comment.add_to_class('likes', GenericRelation(Like))