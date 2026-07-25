from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .user_serializer import (
    UserCreateSerializer, LoginSerializer, UserReadSerializer,
    GetUsersSerializer, UserUpdateSerializer, ChangePasswordSerializer,
)
from .image_serializer import ImageUploadSerializer
from ..services.user import UserServices
from core.storage import R2StorageService
from core.exceptions import ValidationError


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    # 1. Retrieve the refresh token from HttpOnly Cookie
    refresh_token_str = request.COOKIES.get('refresh_token')
    
    # 2. Delegate token validation and rotation to the Service Layer
    try:
        data = UserServices.refresh_token(refresh_token_str)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    # 3. Format the HTTP Response
    response = Response({'access': data['access']}, status=status.HTTP_200_OK)
    
    # If rotated refresh token is returned, update the cookie
    if 'refresh' in data:
        response.set_cookie(
            key='refresh_token',
            value=data['refresh'],
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite='Lax',
            path='/',
        )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = UserServices.create_user(serializer.validated_data)
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        tokens = UserServices.login(serializer.validated_data)
        
        # Only return the access token in the JSON body for XSS safety
        response = Response({'access': tokens['access']}, status=status.HTTP_200_OK)
        
        # Set the refresh token in an HttpOnly, SameSite cookie restricted to /user/token/refresh/ path
        response.set_cookie(
            key='refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite='Lax',
            path='/',
        )
        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_id(request, user_id):
    user = UserServices.get_user_by_id(user_id)
    serializer = UserReadSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_users_by_full_name(request):
    serializer = GetUsersSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    filters = {}
    if 'full_name' in data:
        filters['full_name'] = data['full_name']

    result = UserServices.get_users(
        page=data["page"],
        page_size=data["page_size"],
        filters=filters or None,
    )

    result["users"] = UserReadSerializer(
        result["users"],
        many=True
    ).data

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_profile_image(request):
    """
    Upload or replace the authenticated user's profile image.

    Expects multipart/form-data with an 'image' field.
    DRF's default parsers (JSONParser, FormParser, MultiPartParser) handle
    the multipart parsing — no explicit parser_classes needed.

    Returns the full public URL of the uploaded image.
    """
    serializer = ImageUploadSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        image_file = serializer.validated_data['image']
        filename = UserServices.upload_profile_image(request.user, image_file)
        image_url = R2StorageService.get_image_url(filename)
        return Response({'image_url': image_url}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_profile_image(request):
    """
    Delete the authenticated user's profile image from both R2 and the database.

    No request body needed — operates on the currently authenticated user.
    """
    UserServices.delete_profile_image(request.user)
    return Response({'detail': 'Profile image deleted successfully.'}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    """
    Partial update of the authenticated user's profile data.
    Username (email) cannot be changed.
    """
    serializer = UserUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        updated_user = UserServices.update_user(request.user.id, serializer.validated_data)
        return Response(UserReadSerializer(updated_user).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for the authenticated user.
    Requires old_password verification.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        try:
            UserServices.change_password(
                request.user,
                serializer.validated_data['old_password'],
                serializer.validated_data['new_password'],
            )
            return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Hard-delete the authenticated user's account.
    This is irreversible.
    """
    UserServices.delete_user(request.user)
    return Response({'detail': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
