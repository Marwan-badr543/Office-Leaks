from rest_framework import serializers
from ..db.models import Review
from user.views.user_serializer import UserReadSerializer
from company.views.company_serializer import CompanyReadSerializer


class ReviewCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ['user_id', 'company_id', 'review', 'is_anonymous']


class ReviewUpdateSerializer(serializers.Serializer):
    review = serializers.CharField()


class ReviewReadSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    company = CompanyReadSerializer(read_only=True)
    rate = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'creation', 'review', 'is_anonymous', 'likes_number', 'comments_number', 'user_id', 'company_id', 'user', 'company', 'rate', 'has_liked']

    def get_user(self, obj):
        if obj.is_anonymous:
            return None
        try:
            if obj.user:
                return UserReadSerializer(obj.user).data
        except Exception:
            pass
        return None

    def get_rate(self, obj):
        return getattr(obj, 'user_rate', None)

    def get_has_liked(self, obj):
        return getattr(obj, 'has_liked', False)

    def get_user_id(self, obj):
        if obj.is_anonymous:
            return None
        return obj.user_id


class GetReviewsByCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    page_size = serializers.IntegerField(min_value=1, max_value=100)
    page = serializers.IntegerField(min_value=1)


class DeleteReviewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
