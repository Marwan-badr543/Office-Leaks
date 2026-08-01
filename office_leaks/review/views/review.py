from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .review_serializer import (
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewReadSerializer,
    GetReviewsByCompanySerializer,
    DeleteReviewSerializer,
)
from ..services.review import ReviewServices


@api_view(['POST'])
def create_review(request):
    serializer = ReviewCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        review = ReviewServices.create_review(serializer.validated_data)
        return Response(ReviewReadSerializer(review).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_review(request, review_id):
    serializer = ReviewUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.user.id
        review = ReviewServices.update_review(review_id, user_id, serializer.validated_data)
        return Response(ReviewReadSerializer(review).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reviews_by_company(request):
    serializer = GetReviewsByCompanySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = ReviewServices.get_reviews_by_company(
        company_id=data["company_id"],
        page=data["page"],
        page_size=data["page_size"],
        user=user,
    )

    result["reviews"] = ReviewReadSerializer(
        result["reviews"],
        many=True
    ).data

    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_review_by_id(request, review_id):
    user = request.user if request.user and request.user.is_authenticated else None
    review = ReviewServices.get_review_by_id(review_id, user)
    return Response(ReviewReadSerializer(review).data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_review(request, review_id):
    serializer = DeleteReviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = request.user.id

    review = ReviewServices.delete_review(review_id, user_id)
    return Response(
        {'detail': f'Review {review.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
