from rest_framework import serializers
from user.db.models import User, GenderChoices


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'password',
            'age', 'country', 'gender', 'about', 'current_company',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'about': {'required': False},
            'current_company': {'required': False},
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserReadSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    default_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name', 'age',
            'gender', 'about', 'profile_image', 'profile_image_url',
            'default_avatar_url', 'current_company', 'country', 'user_timezone',
        ]

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            from core.storage import R2StorageService
            return R2StorageService.get_image_url(obj.profile_image)
        return None

    def get_default_avatar_url(self, obj):
        """Return a gender-based default avatar path when no custom image is set."""
        if obj.profile_image:
            return None
        if obj.gender == GenderChoices.FEMALE:
            return '/assets/female_avatar.svg'
        return '/assets/male_avatar.svg'


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    age = serializers.IntegerField(required=False, min_value=0, max_value=150)
    gender = serializers.ChoiceField(choices=GenderChoices.choices, required=False)
    about = serializers.CharField(required=False, max_length=1000, allow_blank=True)
    current_company = serializers.CharField(required=False, max_length=100, allow_blank=True)
    country = serializers.CharField(required=False, max_length=50)
    user_timezone = serializers.CharField(required=False, max_length=50)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class GetUsersSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=True)
    page_size = serializers.IntegerField(required=True)
    full_name = serializers.CharField(required=False, max_length=300)
