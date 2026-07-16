from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .review_like_serializer import (
    ReviewLikeCreateSerializer,
    ReviewLikeReadSerializer,
    DeleteReviewLikeSerializer,
)
from ..services.review_like import ReviewLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = ReviewLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        like = ReviewLikeServices.create_like(serializer.validated_data)
        return Response(ReviewLikeReadSerializer(like).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, like_id):
    serializer = DeleteReviewLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    like = ReviewLikeServices.delete_like(like_id, user_id)
    return Response(
        {'detail': f'Like {like.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
