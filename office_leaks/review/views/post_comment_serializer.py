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
    class Meta:
        model = PostComment
        fields = ['id', 'creation', 'comment', 'likes_number', 'user_id', 'post_id']


class GetPostCommentsSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    page_size = serializers.IntegerField()
    page = serializers.IntegerField()


class DeletePostCommentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
