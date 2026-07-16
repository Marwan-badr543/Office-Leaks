from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.review_like_repo import ReviewLikeRepo
from review.db.repositories.review_repo import ReviewRepo
from core.exceptions import NotFoundError, DuplicateResourceError, ValidationError

User = get_user_model()


class ReviewLikeServices():

    @staticmethod
    def create_like(validated_data):
        user_id = validated_data.get('user_id')
        review_id = validated_data.get('review_id')

        # Validate user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

        # Validate review exists
        if not ReviewRepo.get_review_by_id(review_id):
            raise NotFoundError(f"Review with id {review_id} not found.")

        # Validate duplicate like
        if ReviewLikeRepo.get_like_by_user_and_review(user_id, review_id):
            raise DuplicateResourceError(f"User {user_id} already liked review {review_id}.")

        with transaction.atomic():
            like = ReviewLikeRepo.create_like(validated_data)
            ReviewRepo.increment_likes_count(review_id)
            return like

    @staticmethod
    def delete_like(like_id, user_id):
        like = ReviewLikeRepo.get_like_by_id(like_id)
        if not like:
            raise NotFoundError(f"Like with id {like_id} not found.")

        if like.user_id != user_id:
            raise ValidationError("You can only delete your own likes.")

        review_id = like.review_id

        with transaction.atomic():
            ReviewLikeRepo.delete_like(like)
            ReviewRepo.decrement_likes_count(review_id)
            return like
