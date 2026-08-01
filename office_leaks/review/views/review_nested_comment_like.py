from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .review_nested_comment_like_serializer import (
    ReviewNestedCommentLikeCreateSerializer,
    DeleteReviewNestedCommentLikeSerializer,
)
from ..services.review_nested_comment_like import ReviewNestedCommentLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = ReviewNestedCommentLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        res = ReviewNestedCommentLikeServices.create_like(serializer.validated_data)
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, review_nested_comment_id):
    serializer = DeleteReviewNestedCommentLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = request.user.id

    res = ReviewNestedCommentLikeServices.delete_like(user_id=user_id, comment_id=review_nested_comment_id)
    return Response(res, status=status.HTTP_200_OK)
