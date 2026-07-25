from review.db.models import ReviewCommentLike
from core.exceptions import DatabaseError


class ReviewCommentLikeRepo():

    @staticmethod
    def get_like_by_user_and_comment(user_id, comment_id):
        try:
            return ReviewCommentLike.objects.filter(user_id=user_id, review_comment_id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_comment_like_by_user_and_comment: {e}")

    @staticmethod
    def delete_like(like_obj: ReviewCommentLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_review_comment_like: {e}")

    @staticmethod
    def bulk_create_likes(likes_to_create: list):
        try:
            return ReviewCommentLike.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in bulk_create_review_comment_likes: {e}")

    @staticmethod
    def get_liked_comment_ids_by_user(user_id, comment_ids: list) -> set:
        try:
            return set(
                ReviewCommentLike.objects.filter(
                    user_id=user_id,
                    review_comment_id__in=comment_ids
                ).values_list('review_comment_id', flat=True)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_liked_comment_ids_by_user: {e}")
