from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.post_repo import PostRepo
from review.db.repositories.review_repo import ReviewRepo
from core.exceptions import NotFoundError, DuplicateResourceError, ValidationError


User = get_user_model()


class PostServices():

    @staticmethod
    def create_post(validated_data):
        user_id = validated_data.get('user_id')
        review_id = validated_data.get('review_id')
        content = validated_data.get('content')

        # Validate: can't send both content and review_id
        if content and review_id:
            raise ValidationError("You cannot send both content and review_id. Send one or the other.")

        # Validate: must send at least one
        if not content and not review_id:
            raise ValidationError("You must send either content or review_id.")

        # Check if user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

        # If review posted: validate review exists and check duplicate
        if review_id:
            if not ReviewRepo.get_review_by_id(review_id):
                raise NotFoundError(f"Review with id {review_id} not found.")

            if PostRepo.get_post_by_user_and_review(user_id, review_id):
                raise DuplicateResourceError(f"User {user_id} already posted review {review_id}.")

            # Ensure content is null for review posts
            validated_data.pop('content', None)

        # If content post: ensure review_id is null
        if content:
            validated_data.pop('review_id', None)

        with transaction.atomic():
            return PostRepo.create_post(validated_data)


    @staticmethod
    def update_post(post_id, user_id, validated_data):
        post = PostRepo.get_post_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found.")

        if post.user_id != user_id:
            raise ValidationError("You can only update your own posts.")

        # Only content posts can be updated
        if post.review_id is not None:
            raise ValidationError("Review posts cannot be updated.")

        with transaction.atomic():
            PostRepo.update_post(post_id, validated_data)
            return PostRepo.get_post_by_id(post_id)


    @staticmethod
    def get_posts(page, page_size):
        return PostRepo.get_posts(page, page_size)


    @staticmethod
    def delete_post(post_id, user_id):
        post = PostRepo.get_post_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found.")

        if post.user_id != user_id:
            raise ValidationError("You can only delete your own posts.")

        with transaction.atomic():
            PostRepo.delete_post(post)
            return post
