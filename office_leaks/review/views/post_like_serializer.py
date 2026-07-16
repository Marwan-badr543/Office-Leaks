from rest_framework import serializers
from ..db.models import PostLike


class PostLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PostLike
        fields = ['user_id', 'post_id']


class PostLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['id', 'creation', 'user_id', 'post_id']


class DeletePostLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
