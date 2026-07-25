from review.db.models import PostNestedCommentLike
from core.exceptions import DatabaseError


class PostNestedCommentLikeRepo():

    @staticmethod
    def get_like_by_user_and_comment(user_id, comment_id):
        try:
            return PostNestedCommentLike.objects.filter(user_id=user_id, post_nested_comment_id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_nested_comment_like_by_user_and_comment: {e}")

    @staticmethod
    def delete_like(like_obj: PostNestedCommentLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_post_nested_comment_like: {e}")

    @staticmethod
    def bulk_create_likes(likes_to_create: list):
        try:
            return PostNestedCommentLike.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in bulk_create_post_nested_comment_likes: {e}")

    @staticmethod
    def get_liked_nested_comment_ids_by_user(user_id, nested_comment_ids: list) -> set:
        try:
            return set(
                PostNestedCommentLike.objects.filter(
                    user_id=user_id,
                    post_nested_comment_id__in=nested_comment_ids
                ).values_list('post_nested_comment_id', flat=True)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_liked_nested_comment_ids_by_user: {e}")
