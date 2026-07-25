from django.db.models import F
from review.db.models import Review
from core.exceptions import DatabaseError
from company.db.models import CompanyRate


class ReviewRepo():

    @staticmethod
    def create_review(review_data: dict):
        try:
            review = Review.objects.create(**review_data)
            review = Review.objects.select_related('user', 'company').get(id=review.id)
            rate_obj = CompanyRate.objects.filter(company_id=review.company_id, user_id=review.user_id).first()
            review.user_rate = rate_obj.rate if rate_obj else None
            return review
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_review: {e}")

    @staticmethod
    def get_review_by_id(review_id):
        try:
            review = Review.objects.filter(id=review_id).select_related('user', 'company').first()
            if review:
                rate_obj = CompanyRate.objects.filter(company_id=review.company_id, user_id=review.user_id).first()
                review.user_rate = rate_obj.rate if rate_obj else None
            return review
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_by_id: {e}")

    @staticmethod
    def get_reviews_by_company(company_id, page=1, page_size=10):
        try:
            queryset = Review.objects.filter(company_id=company_id).select_related('user', 'company').order_by('-creation')
            start = (page - 1) * page_size
            end = start + page_size
            reviews = list(queryset[start:end])

            if reviews:
                user_ids = [r.user_id for r in reviews]
                rates = CompanyRate.objects.filter(company_id=company_id, user_id__in=user_ids)
                rate_map = {rate.user_id: rate.rate for rate in rates}
                for r in reviews:
                    r.user_rate = rate_map.get(r.user_id, None)

            return {
                "reviews": reviews,
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
    def increment_likes_count(review_id, count=1):
        try:
            Review.objects.filter(id=review_id).update(likes_number=F('likes_number') + count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(review_id, count=1):
        try:
            Review.objects.filter(id=review_id).update(likes_number=F('likes_number') - count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")



