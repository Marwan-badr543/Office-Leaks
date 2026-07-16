from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.review_comment_like_repo import ReviewCommentLikeRepo
from review.db.repositories.review_comment_repo import ReviewCommentRepo
from core.exceptions import NotFoundError, DuplicateResourceError, ValidationError

User = get_user_model()


class ReviewCommentLikeServices():

    @staticmethod
    def create_like(validated_data):
        user_id = validated_data.get('user_id')
        comment_id = validated_data.get('review_comment_id')

        # Validate user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

        # Validate comment exists
        if not ReviewCommentRepo.get_comment_by_id(comment_id):
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        # Validate duplicate like
        if ReviewCommentLikeRepo.get_like_by_user_and_comment(user_id, comment_id):
            raise DuplicateResourceError(f"User {user_id} already liked comment {comment_id}.")

        with transaction.atomic():
            like = ReviewCommentLikeRepo.create_like(validated_data)
            ReviewCommentRepo.increment_likes_count(comment_id)
            return like

    @staticmethod
    def delete_like(like_id, user_id):
        like = ReviewCommentLikeRepo.get_like_by_id(like_id)
        if not like:
            raise NotFoundError(f"Like with id {like_id} not found.")

        if like.user_id != user_id:
            raise ValidationError("You can only delete your own likes.")

        comment_id = like.review_comment_id

        with transaction.atomic():
            ReviewCommentLikeRepo.delete_like(like)
            ReviewCommentRepo.decrement_likes_count(comment_id)
            return like
