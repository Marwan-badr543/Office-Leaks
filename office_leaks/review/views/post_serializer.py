from rest_framework import serializers
from ..db.models import Post, Review, PostCategory
from user.views.user_serializer import UserReadSerializer
from company.db.models import Company


class NestedCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class PostCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    review_id = serializers.IntegerField(required=False, write_only=True)
    content = serializers.CharField(required=False, allow_blank=True)
    parent_post_id = serializers.IntegerField(required=False, write_only=True)
    company_id = serializers.IntegerField(required=False, write_only=True)
    category = serializers.ChoiceField(choices=PostCategory.choices, required=False)
    is_anonymous = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Post
        fields = [
            'user_id', 'review_id', 'content',
            'parent_post_id', 'company_id', 'category', 'is_anonymous',
        ]


class PostUpdateSerializer(serializers.Serializer):
    content = serializers.CharField()


class NestedReviewSerializer(serializers.ModelSerializer):
    """Used inside PostReadSerializer to return full review data for review posts."""
    has_liked = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'creation', 'review', 'is_anonymous', 'likes_number', 'comments_number', 'user_id', 'company_id', 'has_liked', 'user']

    def get_has_liked(self, obj):
        return getattr(obj, 'has_liked', False)

    def get_user_id(self, obj):
        if obj.is_anonymous:
            return None
        return obj.user_id

    def get_user(self, obj):
        if obj.is_anonymous:
            return None
        try:
            if obj.user:
                return UserReadSerializer(obj.user).data
        except Exception:
            pass
        return None


class NestedParentPostSerializer(serializers.ModelSerializer):
    """Used inside PostReadSerializer to return parent post data for reposts.
    Only one level deep since nested reposts are prevented."""
    review = NestedReviewSerializer(read_only=True)
    company = NestedCompanySerializer(read_only=True)
    has_liked = serializers.SerializerMethodField()
    is_anonymous = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'creation', 'content', 'is_anonymous',
            'likes_number', 'comments_number',
            'user_id', 'review', 'company_id', 'company', 'category', 'has_liked', 'user',
        ]

    def get_has_liked(self, obj):
        return getattr(obj, 'has_liked', False)

    def get_is_anonymous(self, obj):
        if obj.is_anonymous:
            return True
        if obj.review and obj.review.is_anonymous:
            return True
        return False

    def get_user_id(self, obj):
        if obj.is_anonymous or (obj.review and obj.review.is_anonymous):
            return None
        return obj.user_id

    def get_user(self, obj):
        if obj.is_anonymous or (obj.review and obj.review.is_anonymous):
            return None
        try:
            if obj.user:
                return UserReadSerializer(obj.user).data
        except Exception:
            pass
        return None


class PostReadSerializer(serializers.ModelSerializer):
    review = NestedReviewSerializer(read_only=True)
    parent_post = NestedParentPostSerializer(read_only=True)
    company = NestedCompanySerializer(read_only=True)
    has_liked = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    is_anonymous = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'creation', 'content', 'is_anonymous',
            'likes_number', 'comments_number',
            'user_id', 'review', 'parent_post', 'company_id', 'company', 'category', 'has_liked',
            'user',
        ]

    def get_has_liked(self, obj):
        return getattr(obj, 'has_liked', False)

    def get_is_anonymous(self, obj):
        if obj.is_anonymous:
            return True
        if obj.review and obj.review.is_anonymous:
            return True
        return False

    def get_user_id(self, obj):
        if obj.is_anonymous or (obj.review and obj.review.is_anonymous):
            return None
        return obj.user_id

    def get_user(self, obj):
        if obj.is_anonymous or (obj.review and obj.review.is_anonymous):
            return None
        try:
            if obj.user:
                return UserReadSerializer(obj.user).data
        except Exception:
            pass
        return None


class GetPostsSerializer(serializers.Serializer):
    page_size = serializers.IntegerField(min_value=1, max_value=100)
    page = serializers.IntegerField(min_value=1)
    ordering = serializers.ChoiceField(choices=['recent', 'popular'], default='recent', required=False)
    category = serializers.ChoiceField(choices=PostCategory.choices, required=False)


class DeletePostSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
