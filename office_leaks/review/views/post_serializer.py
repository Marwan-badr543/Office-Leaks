from rest_framework import serializers
from ..db.models import Post, Review


class PostCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_id = serializers.IntegerField(required=False, write_only=True)
    content = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Post
        fields = ['user_id', 'review_id', 'content']


class PostUpdateSerializer(serializers.Serializer):
    content = serializers.CharField()


class NestedReviewSerializer(serializers.ModelSerializer):
    """Used inside PostReadSerializer to return full review data for review posts."""
    class Meta:
        model = Review
        fields = ['id', 'creation', 'review', 'is_anonymous', 'likes_number', 'comments_number', 'user_id', 'company_id']


class PostReadSerializer(serializers.ModelSerializer):
    review = NestedReviewSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'creation', 'content', 'likes_number', 'comments_number', 'user_id', 'review']


class GetPostsSerializer(serializers.Serializer):
    page_size = serializers.IntegerField()
    page = serializers.IntegerField()


class DeletePostSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
