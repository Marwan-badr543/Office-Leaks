from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, F
from review.db.models import Post
from core.exceptions import DatabaseError


class PostRepo():

    @staticmethod
    def create_post(post_data: dict):
        try:
            post = Post.objects.create(**post_data)
            return Post.objects.select_related(
                'review', 'review__user', 'parent_post', 'parent_post__user', 'company', 'user'
            ).get(id=post.id)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_post: {e}")

    @staticmethod
    def get_post_by_id(post_id):
        try:
            return Post.objects.select_related(
                'review', 'review__user', 'parent_post', 'parent_post__user', 'company', 'user'
            ).filter(id=post_id).first()
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
    def get_posts(page=1, page_size=10, ordering='recent', category=None):
        try:
            queryset = Post.objects.select_related(
                'review', 'review__user', 'parent_post', 'parent_post__user', 'company', 'user'
            )

            if category:
                queryset = queryset.filter(category=category)

            if ordering == 'popular':
                queryset = queryset.order_by('-popularity_score', '-creation', '-id')
            else:
                queryset = queryset.order_by('-creation')

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
    def increment_likes_count(post_id, count=1):
        try:
            Post.objects.filter(id=post_id).update(
                likes_number=F('likes_number') + count,
                popularity_score=F('popularity_score') + (count * 1)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_likes_count: {e}")

    @staticmethod
    def decrement_likes_count(post_id, count=1):
        try:
            Post.objects.filter(id=post_id).update(
                likes_number=F('likes_number') - count,
                popularity_score=F('popularity_score') - (count * 1)
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_likes_count: {e}")

    @staticmethod
    def increment_popularity_score(post_id, amount=1):
        try:
            Post.objects.filter(id=post_id).update(popularity_score=F('popularity_score') + amount)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in increment_popularity_score: {e}")

    @staticmethod
    def decrement_popularity_score(post_id, amount=1):
        try:
            Post.objects.filter(id=post_id).update(popularity_score=F('popularity_score') - amount)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in decrement_popularity_score: {e}")

    @staticmethod
    def get_posts_by_user(user_id, page=1, page_size=10, ordering='recent'):
        try:
            queryset = Post.objects.filter(user_id=user_id, is_anonymous = False).select_related(
                'review', 'review__user', 'parent_post', 'parent_post__user', 'company', 'user'
            )

            if ordering == 'popular':
                queryset = queryset.order_by('-popularity_score', '-creation')
            else:
                queryset = queryset.order_by('-creation')

            start = (page - 1) * page_size
            end = start + page_size

            return {
                "posts": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_posts_by_user: {e}")

    @staticmethod
    def get_trending_categories(limit=6, days=7):
        try:
            start_date = timezone.now() - timedelta(days=days)
            queryset = (
                Post.objects.filter(creation__gte=start_date, category__isnull=False)
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')[:limit]
            )
            return list(queryset)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_trending_categories: {e}")




