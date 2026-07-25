from django.db.models import F
from review.db.models import PostComment
from core.exceptions import DatabaseError


class PostCommentRepo():

    @staticmethod
    def create_comment(comment_data: dict):
        try:
            comment = PostComment.objects.create(**comment_data)
            return PostComment.objects.select_related('user').get(id=comment.id)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_post_comment: {e}")

    @staticmethod
    def get_comment_by_id(comment_id):
        try:
            return PostComment.objects.select_related('user').filter(id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_comment_by_id: {e}")

    @staticmethod
    def get_comments_by_post(post_id, page=1, page_size=10):
        try:
            queryset = PostComment.objects.select_related('user').filter(post_id=post_id).order_by('-creation')
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "comments": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_comments_by_post: {e}")

    @staticmethod
    def update_comment(comment_id, comment_data: dict):
        try:
            return PostComment.objects.filter(id=comment_id).update(**comment_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_post_comment: {e}")

    @staticmethod
    def delete_comment(comment_obj: PostComment):
        try:
            comment_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_post_comment: {e}")

    @staticmethod
    def increment_likes_count(comment_id, count=1):
        try:
            PostComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') + count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(comment_id, count=1):
        try:
            PostComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') - count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")

