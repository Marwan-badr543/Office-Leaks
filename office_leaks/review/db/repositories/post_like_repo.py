from review.db.models import PostLike
from core.exceptions import DatabaseError


class PostLikeRepo():

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

    @staticmethod
    def bulk_create_likes(likes_to_create: list):
        try:
            return PostLike.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in bulk_create_post_likes: {e}")

    @staticmethod
    def get_liked_post_ids_by_user(user_id, post_ids: list) -> set:
        try:
            return set(
                PostLike.objects.filter(
                    user_id=user_id,
                    post_id__in=post_ids
                ).values_list('post_id', flat=True)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_liked_post_ids_by_user: {e}")

