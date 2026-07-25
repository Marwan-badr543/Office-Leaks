from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..db.models import Company
from .company_serializer import CompanyReadSerializer, CompanyCreateSerializer, CompanyUpdateSerializer, GetCompaniesSerializer, SearchCompaniesSerializer
from .image_serializer import ImageUploadSerializer
from ..services.company import CompanyServices
from core.storage import R2StorageService
from core.exceptions import ValidationError
import os
import logging
from google import genai

logger = logging.getLogger(__name__)



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
@permission_classes([AllowAny])
def get_companies(request):
    serializer = GetCompaniesSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    filters = {
        key: data[key]
        for key in ('name_search', 'industry', 'min_rate', 'max_rate')
        if key in data
    }

    result = CompanyServices.get_companies(
        page=data["page"],
        page_size=10,
        filters=filters or None,
    )

    result["companies"] = CompanyReadSerializer(
        result["companies"],
        many=True
    ).data

    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_companies(request):
    """
    Search companies by name using LIKE '%search_text%'.
    Query param: ?q=search_term
    """
    serializer = SearchCompaniesSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    query_str = serializer.validated_data.get('q', '')

    companies = CompanyServices.search_companies(query_str)
    serialized_companies = CompanyReadSerializer(companies, many=True).data

    return Response({'companies': serialized_companies}, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_company_logo(request, company_id):
    """
    Upload or replace a company's logo.

    Expects multipart/form-data with an 'image' field.
    Validates that the authenticated user owns the company.
    """
    serializer = ImageUploadSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        image_file = serializer.validated_data['image']
        filename = CompanyServices.upload_company_logo(company_id, request.user, image_file)
        image_url = R2StorageService.get_image_url(filename)
        return Response({'image_url': image_url}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_company_logo(request, company_id):
    """
    Delete a company's logo from both R2 and the database.

    Validates that the authenticated user owns the company.
    """
    CompanyServices.delete_company_logo(company_id, request.user)
    return Response({'detail': 'Company logo deleted successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_top_and_trending(request):
    """
    Retrieve top rated companies and trending categories.
    """
    data = CompanyServices.get_top_and_trending()
    # Resolve the logo_url for each top_rated company
    for company in data["top_rated"]:
        if "logo" in company and company["logo"]:
            company["logo_url"] = R2StorageService.get_image_url(company["logo"])
        else:
            company["logo_url"] = None
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company_with_ai(request):
    company_name = request.data.get('company_name')
    if not company_name or not company_name.strip():
        raise ValidationError('Company name is required.')

    company, created = CompanyServices.get_or_create_company_with_ai(
        company_name=company_name,
        user=request.user
    )

    serialized = CompanyReadSerializer(company).data

    if not created:
        return Response({
            'detail': 'Company already exists.',
            'exists': True,
            'company': serialized
        }, status=status.HTTP_200_OK)

    return Response({
        'detail': 'Company created successfully with AI.',
        'company': serialized
    }, status=status.HTTP_201_CREATED)


