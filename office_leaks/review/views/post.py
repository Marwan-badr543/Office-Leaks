from rest_framework.decorators import api_view
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
        post = PostServices.create_post(serializer.validated_data)
        return Response(PostReadSerializer(post).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_post(request, post_id):
    serializer = PostUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user_id = request.data.get('user_id')
        post = PostServices.update_post(post_id, user_id, serializer.validated_data)
        return Response(PostReadSerializer(post).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_posts(request):
    serializer = GetPostsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    result = PostServices.get_posts(
        page=data["page"],
        page_size=data["page_size"],
    )

    result["posts"] = PostReadSerializer(
        result["posts"],
        many=True
    ).data

    return Response(result)


@api_view(['DELETE'])
def delete_post(request, post_id):
    serializer = DeletePostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_id = serializer.validated_data['user_id']

    post = PostServices.delete_post(post_id, user_id)
    return Response(
        {'detail': f'Post {post.id} deleted successfully.'},
        status=status.HTTP_204_NO_CONTENT
    )
