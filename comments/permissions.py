from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a comment to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the comment or admin.
        return obj.author == request.user or request.user.is_staff

class IsCommentAuthorOrPostAuthor(permissions.BasePermission):
    """
    Custom permission to allow comment author or post author to manage comments.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions for comment author, post author, or admin
        return (
            obj.author == request.user or
            obj.post.author == request.user or
            request.user.is_staff
        )