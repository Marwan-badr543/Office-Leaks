from review.db.models import PostLike
from core.exceptions import DatabaseError


class PostLikeRepo():

    @staticmethod
    def create_like(like_data: dict):
        try:
            return PostLike.objects.create(**like_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_post_like: {e}")

    @staticmethod
    def get_like_by_id(like_id):
        try:
            return PostLike.objects.filter(id=like_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_like_by_id: {e}")

    @staticmethod
    def get_like_by_user_and_post(user_id, post_id):
        try:
            return PostLike.objects.filter(user_id=user_id, post_id=post_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_like_by_user_and_post: {e}")

    @staticmethod
    def delete_like(like_obj: PostLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_post_like: {e}")
