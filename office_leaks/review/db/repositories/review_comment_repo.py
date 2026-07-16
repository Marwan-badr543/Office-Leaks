from django.db.models import F
from review.db.models import ReviewComment
from core.exceptions import DatabaseError

class ReviewCommentRepo():

    @staticmethod
    def create_comment(comment_data: dict):
        try:
            return ReviewComment.objects.create(**comment_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_comment: {e}")

    @staticmethod
    def get_comment_by_id(comment_id):
        try:
            return ReviewComment.objects.filter(id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_comment_by_id: {e}")

    @staticmethod
    def get_comments_by_review(review_id, page=1, page_size=10):
        try:
            queryset = ReviewComment.objects.filter(review_id=review_id).order_by('-creation')
            total = queryset.count() if page == 1 else None
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "total": total or 0,
                "comments": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_comments_by_review: {e}")

    @staticmethod
    def update_comment(comment_id, comment_data: dict):
        try:
            return ReviewComment.objects.filter(id=comment_id).update(**comment_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_comment: {e}")

    @staticmethod
    def delete_comment(comment_obj: ReviewComment):
        try:
            comment_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_comment: {e}")

    @staticmethod
    def get_comments_count_by_review(review_id):
        try:
            return ReviewComment.objects.filter(review_id=review_id).count()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_comments_count_by_review: {e}")

    @staticmethod
    def increment_likes_count(comment_id):
        try:
            ReviewComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') + 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(comment_id):
        try:
            ReviewComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') - 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")



