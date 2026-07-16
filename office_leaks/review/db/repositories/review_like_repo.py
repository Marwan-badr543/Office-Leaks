from review.db.models import ReviewLike
from core.exceptions import DatabaseError


class ReviewLikeRepo():

    @staticmethod
    def create_like(like_data: dict):
        try:
            return ReviewLike.objects.create(**like_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_review_like: {e}")

    @staticmethod
    def get_like_by_id(like_id):
        try:
            return ReviewLike.objects.filter(id=like_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_like_by_id: {e}")

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
