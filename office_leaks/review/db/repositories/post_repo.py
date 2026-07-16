from django.db.models import F
from review.db.models import Post
from core.exceptions import DatabaseError


class PostRepo():

    @staticmethod
    def create_post(post_data: dict):
        try:
            return Post.objects.create(**post_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_post: {e}")

    @staticmethod
    def get_post_by_id(post_id):
        try:
            return Post.objects.filter(id=post_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_by_id: {e}")

    @staticmethod
    def get_post_by_user_and_review(user_id, review_id):
        try:
            return Post.objects.filter(user_id=user_id, review_id=review_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_post_by_user_and_review: {e}")

    @staticmethod
    def update_post(post_id, post_data: dict):
        try:
            return Post.objects.filter(id=post_id).update(**post_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_post: {e}")


    @staticmethod
    def get_posts(page=1, page_size=10):
        try:
            queryset = Post.objects.select_related('review').order_by('-creation')
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "posts": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_posts: {e}")


    @staticmethod
    def delete_post(post_obj: Post):
        try:
            post_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_post: {e}")

    @staticmethod
    def increment_comments_count(post_id):
        try:
            Post.objects.filter(id=post_id).update(comments_number=F('comments_number') + 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_comments_count: {e}")

    @staticmethod
    def decrement_comments_count(post_id):
        try:
            Post.objects.filter(id=post_id).update(comments_number=F('comments_number') - 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_comments_count: {e}")

    @staticmethod
    def increment_likes_count(post_id):
        try:
            Post.objects.filter(id=post_id).update(likes_number=F('likes_number') + 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(post_id):
        try:
            Post.objects.filter(id=post_id).update(likes_number=F('likes_number') - 1)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")



