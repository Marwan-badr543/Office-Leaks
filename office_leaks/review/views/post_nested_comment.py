from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .post_nested_comment_serializer import (
    PostNestedCommentCreateSerializer,
    PostNestedCommentUpdateSerializer,
    PostNestedCommentReadSerializer,
    GetPostNestedCommentsSerializer,
    DeletePostNestedCommentSerializer,
)
from ..services.post_nested_comment import PostNestedCommentServices


@api_view(['POST'])
def create_comment(request):
    serializer = PostNestedCommentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        comment = PostNestedCommentServices.create_comment(serializer.validated_data)
        return Response(PostNestedCommentReadSerializer(comment).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_comment(request, comment_id):
    serializer = PostNestedCommentUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.data.get('user_id')
        user = request.user if request.user and request.user.is_authenticated else None
        comment = PostNestedCommentServices.update_comment(comment_id, user_id, serializer.validated_data, user=user)
        return Response(PostNestedCommentReadSerializer(comment).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments_by_parent(request):
    serializer = GetPostNestedCommentsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = PostNestedCommentServices.get_comments_by_parent(
        parent_comment_id=data["parent_comment_id"],
        page=data["page"],
        page_size=data["page_size"],
        user=user,
    )

    result["comments"] = PostNestedCommentReadSerializer(
        result["comments"],
        many=True
    ).data

    return Response(result)


@api_view(['DELETE'])
def delete_comment(request, comment_id):
    serializer = DeletePostNestedCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    comment = PostNestedCommentServices.delete_comment(comment_id, user_id)
    return Response(
        {'detail': f'Nested comment {comment.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )


