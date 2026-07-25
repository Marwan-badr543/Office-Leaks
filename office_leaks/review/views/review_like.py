from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .review_like_serializer import (
    ReviewLikeCreateSerializer,
    DeleteReviewLikeSerializer,
)
from ..services.review_like import ReviewLikeServices


@api_view(['POST'])
def create_like(request):
    serializer = ReviewLikeCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        res = ReviewLikeServices.create_like(serializer.validated_data)
        return Response(res, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_like(request, review_id):
    serializer = DeleteReviewLikeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_id = request.user.id

    res = ReviewLikeServices.delete_like(user_id=user_id, review_id=review_id)
    return Response(res, status=status.HTTP_200_OK)
