from rest_framework import serializers
from ..db.models import CompanyRate

class CompanyRateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    rate = serializers.FloatField(min_value=1.0, max_value=4.0)

    class Meta:
        model = CompanyRate
        fields = ['user_id', 'company_id', 'rate']


class GetCompanyRateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    company_id = serializers.IntegerField()


class CompanyRateReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRate
        fields = ['id', 'creation', 'user_id', 'company_id', 'rate']

    
