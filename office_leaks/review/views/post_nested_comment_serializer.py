from rest_framework import serializers
from ..db.models import PostNestedComment


class PostNestedCommentCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    parent_comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PostNestedComment
        fields = ['user_id', 'parent_comment_id', 'comment_title']


class PostNestedCommentUpdateSerializer(serializers.Serializer):
    comment_title = serializers.CharField()


class PostNestedCommentReadSerializer(serializers.ModelSerializer):
    parent_comment_author_name = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = PostNestedComment
        fields = [
            'id',
            'creation',
            'comment_title',
            'likes_number',
            'user_id',
            'parent_comment_id',
            'parent_comment_author_id',
            'parent_comment_author_name',
            'has_liked',
            'user_name',
            'user_avatar',
        ]

    def get_parent_comment_author_name(self, obj):
        if obj.parent_comment_author:
            return obj.parent_comment_author.full_name
        return None

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



class GetPostNestedCommentsSerializer(serializers.Serializer):
    parent_comment_id = serializers.IntegerField()
    page_size = serializers.IntegerField(min_value=1, max_value=100)
    page = serializers.IntegerField(min_value=1)


class DeletePostNestedCommentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


