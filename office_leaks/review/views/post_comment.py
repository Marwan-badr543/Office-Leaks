from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .post_comment_serializer import (
    PostCommentCreateSerializer,
    PostCommentUpdateSerializer,
    PostCommentReadSerializer,
    GetPostCommentsSerializer,
    DeletePostCommentSerializer,
)
from ..services.post_comment import PostCommentServices


@api_view(['POST'])
def create_comment(request):
    serializer = PostCommentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        comment = PostCommentServices.create_comment(serializer.validated_data)
        return Response(PostCommentReadSerializer(comment).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_comment(request, comment_id):
    serializer = PostCommentUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.user.id
        user = request.user if request.user and request.user.is_authenticated else None
        comment = PostCommentServices.update_comment(comment_id, user_id, serializer.validated_data, user=user)
        return Response(PostCommentReadSerializer(comment).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments_by_post(request):
    serializer = GetPostCommentsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = PostCommentServices.get_comments_by_post(
        post_id=data["post_id"],
        page=data["page"],
        page_size=data["page_size"],
        user=user,
    )

    result["comments"] = PostCommentReadSerializer(
        result["comments"],
        many=True
    ).data

    return Response(result)


@api_view(['DELETE'])
def delete_comment(request, comment_id):
    serializer = DeletePostCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = request.user.id

    comment = PostCommentServices.delete_comment(comment_id, user_id)
    return Response(
        {'detail': f'Comment {comment.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
