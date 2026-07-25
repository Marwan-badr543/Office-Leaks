from collections import abc
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .rate_serializer import CompanyRateSerializer, GetCompanyRateSerializer, CompanyRateReadSerializer
from ..services.company_rate import CompanyRateServices


@api_view(['POST'])
def create_company_rate(request):
    serializer = CompanyRateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        current_rate, created = CompanyRateServices.update_or_create_company_rate(serializer.validated_data)
        if created:
            return Response({"message": "Rate value created successfully",
                            "current_rate": current_rate},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Rate value updated successfully",
                            "current_rate": current_rate},
                            status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_rate(request):
    serializer = GetCompanyRateSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    
    user_id = serializer.validated_data['user_id']
    company_id = serializer.validated_data['company_id']
    
    rate = CompanyRateServices.get_company_rate(user_id, company_id)
    read_serializer = CompanyRateReadSerializer(rate)
    return Response(read_serializer.data, status=status.HTTP_200_OK)




