from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .post_like_serializer import (
    PostLikeCreateSerializer,
    PostLikeReadSerializer,
    DeletePostLikeSerializer,
)
from ..services.post_like import PostLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = PostLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        like = PostLikeServices.create_like(serializer.validated_data)
        return Response(PostLikeReadSerializer(like).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, like_id):
    serializer = DeletePostLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    like = PostLikeServices.delete_like(like_id, user_id)
    return Response(
        {'detail': f'Like {like.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
