from rest_framework import serializers
from ..db.models import PostNestedCommentLike


class PostNestedCommentLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    post_nested_comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PostNestedCommentLike
        fields = ['user_id', 'post_nested_comment_id']


class PostNestedCommentLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNestedCommentLike
        fields = ['id', 'creation', 'user_id', 'post_nested_comment_id']


class DeletePostNestedCommentLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
