from rest_framework import serializers
from ..db.models import ReviewNestedCommentLike


class ReviewNestedCommentLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_nested_comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReviewNestedCommentLike
        fields = ['user_id', 'review_nested_comment_id']


class ReviewNestedCommentLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewNestedCommentLike
        fields = ['id', 'creation', 'user_id', 'review_nested_comment_id']


class DeleteReviewNestedCommentLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
