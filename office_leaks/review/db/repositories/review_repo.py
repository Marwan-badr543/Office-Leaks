from django.db.models import F
from review.db.models import Review
from core.exceptions import DatabaseError


class ReviewRepo():

    @staticmethod
    def create_review(review_data: dict):
        try:
            return Review.objects.create(**review_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_review: {e}")

    @staticmethod
    def get_review_by_id(review_id):
        try:
            return Review.objects.filter(id=review_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_by_id: {e}")

    @staticmethod
    def get_reviews_by_company(company_id, page=1, page_size=10):
        try:
            queryset = Review.objects.filter(company_id=company_id).order_by('-creation')
            total = queryset.count() if page == 1 else None
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "total": total or 0,
                "reviews": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_reviews_by_company: {e}")


    @staticmethod
    def update_review(review_id, review_data: dict):
        try:
            return Review.objects.filter(id=review_id).update(**review_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_review: {e}")


    @staticmethod
    def delete_review(review_obj: Review):
        try:
            review_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_review: {e}")


    @staticmethod
    def increment_comments_count(review_id):
        try:
            Review.objects.filter(id=review_id).update(comments_number=F('comments_number') + 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_comments_count: {e}")


    @staticmethod
    def decrement_comments_count(review_id):
        try:
            Review.objects.filter(id=review_id).update(comments_number=F('comments_number') - 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_comments_count: {e}")

    @staticmethod
    def increment_likes_count(review_id):
        try:
            Review.objects.filter(id=review_id).update(likes_number=F('likes_number') + 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(review_id):
        try:
            Review.objects.filter(id=review_id).update(likes_number=F('likes_number') - 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")



