from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from ..db.models import Company
from rest_framework.pagination import PageNumberPagination


class CompanyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'creation', 'name', 'address', 'industry', 'logo', 'founded_at', 'website', 'linkedin', 'instagram', 'facebook', 'current_rate']



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
    page_size = serializers.IntegerField()
    page = serializers.IntegerField()


