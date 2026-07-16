from review.db.models import PostCommentLike
from core.exceptions import DatabaseError


class PostCommentLikeRepo():

    @staticmethod
    def create_like(like_data: dict):
        try:
            return PostCommentLike.objects.create(**like_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_post_comment_like: {e}")

    @staticmethod
    def get_like_by_id(like_id):
        try:
            return PostCommentLike.objects.filter(id=like_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_comment_like_by_id: {e}")

    @staticmethod
    def get_like_by_user_and_comment(user_id, comment_id):
        try:
            return PostCommentLike.objects.filter(user_id=user_id, post_comment_id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_comment_like_by_user_and_comment: {e}")

    @staticmethod
    def delete_like(like_obj: PostCommentLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_post_comment_like: {e}")
