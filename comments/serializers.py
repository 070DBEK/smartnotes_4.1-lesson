from rest_framework import serializers
from .models import Comment
from users.serializers import UserSerializer
from posts.models import Like

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'parent', 'created_at',
            'updated_at', 'is_active', 'likes_count', 'replies_count',
            'is_liked', 'replies'
        ]
        read_only_fields = ['id', 'author', 'post', 'created_at', 'updated_at', 'is_active']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False

    def get_replies(self, obj):
        if obj.parent is None:  # Only show replies for top-level comments
            replies = obj.get_replies()
            return CommentReplySerializer(replies, many=True, context=self.context).data
        return []

class CommentReplySerializer(serializers.ModelSerializer):
    """Simplified serializer for replies to avoid deep nesting"""
    author = UserSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'created_at', 'updated_at',
            'likes_count', 'is_liked'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Comment content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment cannot exceed 1000 characters.")
        return value.strip()

    def validate_parent(self, value):
        if value:
            # Check if parent comment exists and belongs to the same post
            post_id = self.context['post_id']
            if value.post.id != post_id:
                raise serializers.ValidationError("Parent comment must belong to the same post.")
            if not value.is_active:
                raise serializers.ValidationError("Cannot reply to an inactive comment.")
            # Prevent deep nesting (only allow one level of replies)
            if value.parent is not None:
                raise serializers.ValidationError("Cannot reply to a reply. Please reply to the original comment.")
        return value

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Comment content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment cannot exceed 1000 characters.")
        return value.strip()

class CommentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    author = serializers.StringRelatedField()
    likes_count = serializers.ReadOnlyField()
    replies_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'created_at', 'likes_count',
            'replies_count', 'is_liked', 'parent'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False