from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.review_comment_repo import ReviewCommentRepo
from review.db.repositories.review_repo import ReviewRepo
from core.exceptions import NotFoundError, ValidationError

User = get_user_model()

class CommentServices():

    @staticmethod
    def validate_user_and_review_exist(user_id, review_id):
        if not ReviewRepo.get_review_by_id(review_id):
            raise NotFoundError(f"Review with id {review_id} not found.")

        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")


    @staticmethod
    def create_comment(validated_data):
        user_id = validated_data.get('user_id')
        review_id = validated_data.get('review_id')

        CommentServices.validate_user_and_review_exist(user_id, review_id)

        with transaction.atomic():
            comment = ReviewCommentRepo.create_comment(validated_data)
            ReviewRepo.increment_comments_count(review_id)
            return comment


    @staticmethod
    def update_comment(comment_id, user_id, validated_data):
        comment = ReviewCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only update your own comments.")

        with transaction.atomic():
            ReviewCommentRepo.update_comment(comment_id, validated_data)
            return ReviewCommentRepo.get_comment_by_id(comment_id)


    @staticmethod
    def get_comments_by_review(review_id, page, page_size):
        if not ReviewRepo.get_review_by_id(review_id):
            raise NotFoundError(f"Review with id {review_id} not found.")

        return ReviewCommentRepo.get_comments_by_review(review_id, page, page_size)

    @staticmethod
    def delete_comment(comment_id, user_id):
        comment = ReviewCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only delete your own comments.")

        review_id = comment.review_id

        with transaction.atomic():
            ReviewCommentRepo.delete_comment(comment)
            ReviewRepo.decrement_comments_count(review_id)
            return comment


