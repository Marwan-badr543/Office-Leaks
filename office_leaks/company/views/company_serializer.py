from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from ..db.models import Company
from rest_framework.pagination import PageNumberPagination
from core.storage import R2StorageService


class CompanyReadSerializer(serializers.ModelSerializer):
    # SerializerMethodField is a read-only field that calls get_<field_name>()
    # to compute its value during serialization. We use it here to transform
    # the stored UUID filename into a full public URL on every read.
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'creation', 'name', 'address', 'industry', 'logo_url', 'founded_at', 'website', 'linkedin', 'instagram', 'facebook', 'current_rate']

    def get_logo_url(self, obj):
        """
        Convert the UUID filename stored in obj.logo to a full public URL.
        Returns None if the company has no logo set.
        """
        return R2StorageService.get_image_url(obj.logo)



class CompanyCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Company
        fields = ['user_id', 'name', 'address', 'industry', 'founded_at', 'website', 'linkedin', 'instagram', 'facebook']
    


class CompanyUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=100)
    address = serializers.CharField(required=False, max_length=300)
    industry = serializers.CharField(required=False, max_length=50)
    founded_at = serializers.DateField(required=False)
    website = serializers.CharField(required=False, max_length=100)
    linkedin = serializers.CharField(required=False, max_length=100)
    instagram = serializers.CharField(required=False, max_length=100)
    facebook = serializers.CharField(required=False, max_length=100)


class GetCompaniesSerializer(serializers.Serializer):
    page_size = serializers.IntegerField(min_value=1, max_value=100)
    page = serializers.IntegerField(min_value=1)
    name_search = serializers.CharField(required=False, max_length=100)
    industry = serializers.CharField(required=False, max_length=50)
    min_rate = serializers.FloatField(required=False, min_value=0, max_value=4)
    max_rate = serializers.FloatField(required=False, min_value=0, max_value=4)


class SearchCompaniesSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, default='', allow_blank=True, max_length=100)




