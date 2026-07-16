from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.post_like_repo import PostLikeRepo
from review.db.repositories.post_repo import PostRepo
from core.exceptions import NotFoundError, DuplicateResourceError, ValidationError

User = get_user_model()


class PostLikeServices():

    @staticmethod
    def create_like(validated_data):
        user_id = validated_data.get('user_id')
        post_id = validated_data.get('post_id')

        # Validate user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

        # Validate post exists
        if not PostRepo.get_post_by_id(post_id):
            raise NotFoundError(f"Post with id {post_id} not found.")

        # Validate duplicate like
        if PostLikeRepo.get_like_by_user_and_post(user_id, post_id):
            raise DuplicateResourceError(f"User {user_id} already liked post {post_id}.")

        with transaction.atomic():
            like = PostLikeRepo.create_like(validated_data)
            PostRepo.increment_likes_count(post_id)
            return like

    @staticmethod
    def delete_like(like_id, user_id):
        like = PostLikeRepo.get_like_by_id(like_id)
        if not like:
            raise NotFoundError(f"Like with id {like_id} not found.")

        if like.user_id != user_id:
            raise ValidationError("You can only delete your own likes.")

        post_id = like.post_id

        with transaction.atomic():
            PostLikeRepo.delete_like(like)
            PostRepo.decrement_likes_count(post_id)
            return like
