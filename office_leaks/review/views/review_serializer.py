from rest_framework import serializers
from ..db.models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ['user_id', 'company_id', 'review', 'is_anonymous']


class ReviewUpdateSerializer(serializers.Serializer):
    review = serializers.CharField()


class ReviewReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'creation', 'review', 'is_anonymous', 'likes_number', 'comments_number', 'user_id', 'company_id']


class GetReviewsByCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    page_size = serializers.IntegerField()
    page = serializers.IntegerField()


class DeleteReviewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
