from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .post_comment_like_serializer import (
    PostCommentLikeCreateSerializer,
    DeletePostCommentLikeSerializer,
)
from ..services.post_comment_like import PostCommentLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = PostCommentLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        res = PostCommentLikeServices.create_like(serializer.validated_data)
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, post_comment_id):
    serializer = DeletePostCommentLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = serializer.validated_data['user_id']

    res = PostCommentLikeServices.delete_like(user_id=user_id, comment_id=post_comment_id)
    return Response(res, status=status.HTTP_200_OK)
