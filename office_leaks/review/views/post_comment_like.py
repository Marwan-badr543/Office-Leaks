from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .post_comment_like_serializer import (
    PostCommentLikeCreateSerializer,
    PostCommentLikeReadSerializer,
    DeletePostCommentLikeSerializer,
)
from ..services.post_comment_like import PostCommentLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = PostCommentLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        like = PostCommentLikeServices.create_like(serializer.validated_data)
        return Response(PostCommentLikeReadSerializer(like).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, like_id):
    serializer = DeletePostCommentLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    like = PostCommentLikeServices.delete_like(like_id, user_id)
    return Response(
        {'detail': f'Like {like.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
