from django.db.models import F
from review.db.models import ReviewNestedComment
from core.exceptions import DatabaseError


class ReviewNestedCommentRepo():

    @staticmethod
    def create_comment(comment_data: dict):
        try:
            comment = ReviewNestedComment.objects.create(**comment_data)
            return ReviewNestedComment.objects.select_related('user', 'parent_comment_author').get(id=comment.id)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_review_nested_comment: {e}")

    @staticmethod
    def get_comment_by_id(comment_id):
        try:
            return ReviewNestedComment.objects.select_related('user', 'parent_comment_author').filter(id=comment_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_nested_comment_by_id: {e}")

    @staticmethod
    def get_comments_by_parent(parent_comment_id, page=1, page_size=10):
        try:
            queryset = ReviewNestedComment.objects.filter(
                parent_comment_id=parent_comment_id
            ).select_related('user', 'parent_comment_author').order_by('-creation')
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "comments": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_review_nested_comments_by_parent: {e}")

    @staticmethod
    def update_comment(comment_id, comment_data: dict):
        try:
            return ReviewNestedComment.objects.filter(id=comment_id).update(**comment_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_review_nested_comment: {e}")

    @staticmethod
    def delete_comment(comment_obj: ReviewNestedComment):
        try:
            comment_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_review_nested_comment: {e}")

    @staticmethod
    def increment_likes_count(comment_id, count=1):
        try:
            ReviewNestedComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') + count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(comment_id, count=1):
        try:
            ReviewNestedComment.objects.filter(id=comment_id).update(likes_number=F('likes_number') - count)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")


