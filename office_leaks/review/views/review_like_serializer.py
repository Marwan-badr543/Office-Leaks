from rest_framework import serializers
from ..db.models import ReviewLike


class ReviewLikeCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReviewLike
        fields = ['user_id', 'review_id']


class ReviewLikeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLike
        fields = ['id', 'creation', 'user_id', 'review_id']


class DeleteReviewLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
