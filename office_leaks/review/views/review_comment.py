from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .review_comment_serializer import (
    ReviewCommentCreateSerializer,
    ReviewCommentUpdateSerializer,
    ReviewCommentReadSerializer,
    GetReviewCommentsSerializer,
    DeleteReviewCommentSerializer,
)
from ..services.review_comment import CommentServices


@api_view(['POST'])
def create_comment(request):
    serializer = ReviewCommentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        comment = CommentServices.create_comment(serializer.validated_data)
        return Response(ReviewCommentReadSerializer(comment).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_comment(request, comment_id):
    serializer = ReviewCommentUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.data.get('user_id')
        user = request.user if request.user and request.user.is_authenticated else None
        comment = CommentServices.update_comment(comment_id, user_id, serializer.validated_data, user=user)
        return Response(ReviewCommentReadSerializer(comment).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_comments_by_review(request):
    serializer = GetReviewCommentsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = CommentServices.get_comments_by_review(
        review_id=data["review_id"],
        page=data["page"],
        page_size=data["page_size"],
        user=user,
    )

    result["comments"] = ReviewCommentReadSerializer(
        result["comments"],
        many=True
    ).data

    return Response(result)


@api_view(['DELETE'])
def delete_comment(request, comment_id):
    serializer = DeleteReviewCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    comment = CommentServices.delete_comment(comment_id, user_id)
    return Response(
        {'detail': f'Comment {comment.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )

