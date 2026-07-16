from rest_framework import serializers
from ..db.models import ReviewComment

class ReviewCommentCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReviewComment
        fields = ['user_id', 'review_id', 'comment']


class ReviewCommentUpdateSerializer(serializers.Serializer):
    comment = serializers.CharField()


class ReviewCommentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ['id', 'creation', 'comment', 'likes_number', 'user_id', 'review_id']


class GetReviewCommentsSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    page_size = serializers.IntegerField()
    page = serializers.IntegerField()


class DeleteReviewCommentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

