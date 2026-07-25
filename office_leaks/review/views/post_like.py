from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .post_like_serializer import (
    PostLikeCreateSerializer,
    DeletePostLikeSerializer,
)
from ..services.post_like import PostLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = PostLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        res = PostLikeServices.create_like(serializer.validated_data)
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, post_id):
    serializer = DeletePostLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = request.user.id

    res = PostLikeServices.delete_like(user_id=user_id, post_id=post_id)
    return Response(res, status=status.HTTP_200_OK)
