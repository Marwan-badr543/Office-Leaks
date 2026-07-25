from review.db.models import ReviewLike
from core.exceptions import DatabaseError


class ReviewLikeRepo():

    @staticmethod
    def get_like_by_user_and_review(user_id, review_id):
        try:
            return ReviewLike.objects.filter(user_id=user_id, review_id=review_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_like_by_user_and_review: {e}")

    @staticmethod
    def delete_like(like_obj: ReviewLike):
        try:
            like_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_review_like: {e}")

    @staticmethod
    def bulk_create_likes(likes_to_create: list):
        try:
            return ReviewLike.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in bulk_create_review_likes: {e}")

    @staticmethod
    def get_liked_review_ids_by_user(user_id, review_ids: list) -> set:
        try:
            return set(
                ReviewLike.objects.filter(
                    user_id=user_id,
                    review_id__in=review_ids
                ).values_list('review_id', flat=True)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_liked_review_ids_by_user: {e}")

