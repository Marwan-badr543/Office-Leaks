from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.post_comment_repo import PostCommentRepo
from review.db.repositories.post_repo import PostRepo
from core.exceptions import NotFoundError, ValidationError

User = get_user_model()


class PostCommentServices():

    @staticmethod
    def validate_user_and_post_exist(user_id, post_id):
        if not PostRepo.get_post_by_id(post_id):
            raise NotFoundError(f"Post with id {post_id} not found.")

        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

    @staticmethod
    def create_comment(validated_data):
        user_id = validated_data.get('user_id')
        post_id = validated_data.get('post_id')

        PostCommentServices.validate_user_and_post_exist(user_id, post_id)

        with transaction.atomic():
            comment = PostCommentRepo.create_comment(validated_data)
            PostRepo.increment_comments_count(post_id)
            return comment

    @staticmethod
    def update_comment(comment_id, user_id, validated_data):
        comment = PostCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only update your own comments.")

        with transaction.atomic():
            PostCommentRepo.update_comment(comment_id, validated_data)
            return PostCommentRepo.get_comment_by_id(comment_id)


    @staticmethod
    def get_comments_by_post(post_id, page, page_size):
        if not PostRepo.get_post_by_id(post_id):
            raise NotFoundError(f"Post with id {post_id} not found.")

        return PostCommentRepo.get_comments_by_post(post_id, page, page_size)


    @staticmethod
    def delete_comment(comment_id, user_id):
        comment = PostCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only delete your own comments.")

        post_id = comment.post_id

        with transaction.atomic():
            PostCommentRepo.delete_comment(comment)
            PostRepo.decrement_comments_count(post_id)
            return comment
