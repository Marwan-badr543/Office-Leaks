from rest_framework import serializers
from ..db.models import PostComment


class PostCommentCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PostComment
        fields = ['user_id', 'post_id', 'comment']


class PostCommentUpdateSerializer(serializers.Serializer):
    comment = serializers.CharField()


class PostCommentReadSerializer(serializers.ModelSerializer):
    has_liked = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ['id', 'creation', 'comment', 'likes_number', 'user_id', 'post_id', 'has_liked', 'user_name', 'user_avatar', 'replies_count']

    def get_replies_count(self, obj) -> int:
        return obj.nested_comments.count()

    def get_has_liked(self, obj):
        return getattr(obj, 'has_liked', False)

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.full_name
        return None

    def get_user_avatar(self, obj):
        if obj.user and obj.user.profile_image:
            from core.storage import R2StorageService
            return R2StorageService.get_image_url(obj.user.profile_image)
        return None


class GetPostCommentsSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    page_size = serializers.IntegerField(min_value=1, max_value=100)
    page = serializers.IntegerField(min_value=1)


class DeletePostCommentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
