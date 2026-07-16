from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .user_serializer import UserCreateSerializer, LoginSerializer
from ..services.user import UserServices


@api_view(['POST'])
def create_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = UserServices.create_user(serializer.validated_data)
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        tokens = UserServices.login(serializer.validated_data)
        return Response(tokens, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
