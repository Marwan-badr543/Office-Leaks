from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..db.models import Company
from .company_serializer import CompanyReadSerializer, CompanyCreateSerializer, CompanyUpdateSerializer, GetCompaniesSerializer
from ..services.company import CompanyServices

@api_view(['POST'])
def create_company(request):
    serializer = CompanyCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        cmpny_created = CompanyServices.create_company(serializer.validated_data)
        return Response({'id': cmpny_created.id, 'name': cmpny_created.name}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_company(request, company_id):    
    serializer = CompanyUpdateSerializer(data=request.data)
    if serializer.is_valid():
        CompanyServices.update_company(company_id, serializer.validated_data)
        return Response({'id': company_id, 'name': serializer.validated_data.get("name")}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_company(request, company_id):
    company = CompanyServices.delete_company(company_id)
    return Response({'detail': f'Company {company.name} deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_companies(request):
    serializer = GetCompaniesSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    result = CompanyServices.get_companies(
        page=data["page"],
        page_size=data["page_size"],
    )

    result["companies"] = CompanyReadSerializer(
        result["companies"],
        many=True
    ).data

    return Response(result)



