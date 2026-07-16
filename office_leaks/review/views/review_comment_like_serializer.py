from rest_framework import serializers
from ..db.models import ReviewCommentLike


class ReviewCommentLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReviewCommentLike
        fields = ['user_id', 'review_comment_id']


class ReviewCommentLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewCommentLike
        fields = ['id', 'creation', 'user_id', 'review_comment_id']


class DeleteReviewCommentLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
