from review.db.models import ReviewNestedCommentLike
from core.exceptions import DatabaseError


class ReviewNestedCommentLikeRepo():

    @staticmethod
    def get_like_by_user_and_comment(user_id, comment_id):
        try:
            return ReviewNestedCommentLike.objects.filter(user_id=user_id, review_nested_comment_id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_nested_comment_like_by_user_and_comment: {e}")

    @staticmethod
    def delete_like(like_obj: ReviewNestedCommentLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_review_nested_comment_like: {e}")

    @staticmethod
    def bulk_create_likes(likes_to_create: list):
        try:
            return ReviewNestedCommentLike.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in bulk_create_review_nested_comment_likes: {e}")

    @staticmethod
    def get_liked_nested_comment_ids_by_user(user_id, nested_comment_ids: list) -> set:
        try:
            return set(
                ReviewNestedCommentLike.objects.filter(
                    user_id=user_id,
                    review_nested_comment_id__in=nested_comment_ids
                ).values_list('review_nested_comment_id', flat=True)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_liked_nested_comment_ids_by_user: {e}")
