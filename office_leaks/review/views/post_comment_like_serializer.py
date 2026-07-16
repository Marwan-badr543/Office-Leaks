from rest_framework import serializers
from ..db.models import PostCommentLike


class PostCommentLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    post_comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PostCommentLike
        fields = ['user_id', 'post_comment_id']


class PostCommentLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentLike
        fields = ['id', 'creation', 'user_id', 'post_comment_id']


class DeletePostCommentLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
