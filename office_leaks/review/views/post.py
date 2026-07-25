from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .post_serializer import (
    PostCreateSerializer,
    PostUpdateSerializer,
    PostReadSerializer,
    GetPostsSerializer,
    DeletePostSerializer,
)
from ..services.post import PostServices


@api_view(['POST'])
def create_post(request):
    serializer = PostCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_id'] = request.user.id
        post = PostServices.create_post(serializer.validated_data)
        return Response(PostReadSerializer(post).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_post(request, post_id):
    serializer = PostUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.user.id
        user = request.user if request.user and request.user.is_authenticated else None
        post = PostServices.update_post(post_id, user_id, serializer.validated_data, user=user)
        return Response(PostReadSerializer(post).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_posts(request):
    serializer = GetPostsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = PostServices.get_posts(
        page=data["page"],
        page_size=10,
        ordering=data.get("ordering", "recent"),
        category=data.get("category"),
        user=user,
    )

    result["posts"] = PostReadSerializer(
        result["posts"],
        many=True
    ).data

    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_posts_by_user(request, user_id):
    serializer = GetPostsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user and request.user.is_authenticated else None

    result = PostServices.get_posts_by_user(
        user_id=user_id,
        page=data["page"],
        page_size=data["page_size"],
        ordering=data.get("ordering", "recent"),
        user=user,
    )

    result["posts"] = PostReadSerializer(
        result["posts"],
        many=True
    ).data

    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_by_id(request, post_id):
    user = request.user if request.user and request.user.is_authenticated else None
    post = PostServices.get_post_by_id(post_id, user=user)
    return Response(PostReadSerializer(post).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_topics(request):
    result = PostServices.get_trending_topics()
    return Response(result, status=status.HTTP_200_OK)




@api_view(['DELETE'])
def delete_post(request, post_id):
    serializer = DeletePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = request.user.id

    post = PostServices.delete_post(post_id, user_id)
    return Response(
        {'detail': f'Post {post.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )