import logging
import json
import redis
from django.db import transaction
from django.contrib.auth import get_user_model
from core.redis_client import get_redis_client
from review.db.repositories.post_repo import PostRepo
from review.db.repositories.review_repo import ReviewRepo
from company.db.repositories.company_repo import CompanyRepo
from core.exceptions import NotFoundError, DuplicateResourceError, ValidationError

logger = logging.getLogger(__name__)


User = get_user_model()


class PostServices():

    @staticmethod
    def create_post(validated_data):
        user_id = validated_data.get('user_id')
        review_id = validated_data.get('review_id')
        content = validated_data.get('content')
        parent_post_id = validated_data.get('parent_post_id')
        company_id = validated_data.get('company_id')

        # Validate: can't send both parent_post_id and review_id
        if parent_post_id and review_id:
            raise ValidationError("You cannot send both parent_post_id and review_id.")

        # Validate: must send at least one of content, review_id, or parent_post_id
        if not content and not review_id and not parent_post_id:
            raise ValidationError("You must send either content, review_id, or parent_post_id.")

        # Check if user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

        # If company mentioned, validate it exists
        if company_id:
            if not CompanyRepo.get_company_with_id(company_id):
                raise NotFoundError(f"Company with id {company_id} not found.")

        # If repost: validate parent post
        if parent_post_id:
            parent_post = PostRepo.get_post_by_id(parent_post_id)
            if not parent_post:
                raise NotFoundError(f"Post with id {parent_post_id} not found.")

            # Prevent nested reposts
            if parent_post.parent_post_id is not None:
                raise ValidationError("Cannot repost a reposted post.")

            # Prevent reposting review posts
            if parent_post.review_id is not None:
                raise ValidationError("Cannot repost a review post.")

        # If review posted: validate review exists and check duplicate
        if review_id:
            if not ReviewRepo.get_review_by_id(review_id):
                raise NotFoundError(f"Review with id {review_id} not found.")

        with transaction.atomic():
            post = PostRepo.create_post(validated_data)

        post.has_liked = False
        return post


    @staticmethod
    def update_post(post_id, user_id, validated_data, user=None):
        post = PostRepo.get_post_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found.")

        if post.user_id != user_id:
            raise ValidationError("You can only update your own posts.")

        with transaction.atomic():
            update_data = {'content': validated_data['content']}
            PostRepo.update_post(post_id, update_data)

        return PostServices.get_post_by_id(post_id, user=user)


    @staticmethod
    def get_posts(page, page_size, ordering='recent', category=None, user=None):
        db_result = PostRepo.get_posts(page, page_size, ordering, category)
        posts = db_result.get("posts", [])
        PostServices._decorate_posts_likes_and_status(posts, user)
        return {"posts": posts}

    @staticmethod
    def get_post_by_id(post_id, user=None):
        post = PostRepo.get_post_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found.")
        PostServices._decorate_posts_likes_and_status([post], user)
        return post

    @staticmethod
    def get_posts_by_user(user_id, page, page_size, ordering='recent', user=None):
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")
        result = PostRepo.get_posts_by_user(user_id, page, page_size, ordering)
        posts = result.get("posts", [])
        PostServices._decorate_posts_likes_and_status(posts, user)
        return result


    @staticmethod
    def delete_post(post_id, user_id):
        post = PostRepo.get_post_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post with id {post_id} not found.")

        if post.user_id != user_id:
            raise ValidationError("You can only delete your own posts.")

        with transaction.atomic():
            PostRepo.delete_post(post)

        return post

    @staticmethod
    def get_trending_categories(limit=6):
        return PostRepo.get_trending_categories(limit)

    @staticmethod
    def _get_trending_topics_from_redis():
        try:
            r = get_redis_client()
            cached_data = r.get("post:trending_categories")
            if not cached_data:
                return None
            return json.loads(cached_data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Redis fetch failed for trending categories: {e}")
            raise ExternalServiceError(f"ExternalServiceError in Redis read: {e}")

    @staticmethod
    def get_trending_topics(limit=6):
        try:
            trending = PostServices._get_trending_topics_from_redis()
            if trending:
                return trending
        except ExternalServiceError as e:
            logger.error(f"Fallback to DB for trending topics due to Redis failure: {e}")

        return PostRepo.get_trending_categories(limit)

    @staticmethod
    def _decorate_posts_likes_and_status(posts, user):
        if not posts:
            return

        post_ids = [p.id for p in posts]

        from collections import Counter
        redis_likes_count = Counter()
        try:
            r = get_redis_client()
            members = r.smembers("global_post_likes_buffer")
            if members:
                for m in members:
                    try:
                        item_str = m if isinstance(m, str) else m.decode()
                        _, p_id_str = item_str.split(':')
                        redis_likes_count[int(p_id_str)] += 1
                    except Exception:
                        continue
        except Exception:
            pass

        liked_post_ids = set()
        if user and user.is_authenticated:
            from review.db.repositories.post_like_repo import PostLikeRepo
            liked_in_db = PostLikeRepo.get_liked_post_ids_by_user(user.id, post_ids)

            liked_in_redis = set()
            try:
                r = get_redis_client()
                pipe = r.pipeline()
                for p_id in post_ids:
                    pipe.sismember("global_post_likes_buffer", f"{user.id}:{p_id}")
                results = pipe.execute()
                for p_id, is_member in zip(post_ids, results):
                    if is_member:
                        liked_in_redis.add(p_id)
            except Exception:
                pass

            liked_post_ids = liked_in_db.union(liked_in_redis)

        for p in posts:
            p.likes_number += redis_likes_count.get(p.id, 0)
            p.has_liked = p.id in liked_post_ids

            if getattr(p, "review", None):
                rev = p.review
                pending_review_likes = 0
                try:
                    r = get_redis_client()
                    rev_members = r.smembers("global_review_likes_buffer")
                    if rev_members:
                        for m in rev_members:
                            try:
                                item_str = m if isinstance(m, str) else m.decode()
                                _, r_id_str = item_str.split(':')
                                if int(r_id_str) == rev.id:
                                    pending_review_likes += 1
                            except Exception:
                                continue
                except Exception:
                    pass
                rev.likes_number += pending_review_likes

                rev_has_liked = False
                if user and user.is_authenticated:
                    from review.db.repositories.review_like_repo import ReviewLikeRepo
                    rev_liked_in_db = ReviewLikeRepo.get_liked_review_ids_by_user(user.id, [rev.id])
                    rev_liked_in_redis = False
                    try:
                        r = get_redis_client()
                        rev_liked_in_redis = bool(r.sismember("global_review_likes_buffer", f"{user.id}:{rev.id}"))
                    except Exception:
                        pass
                    rev_has_liked = (rev.id in rev_liked_in_db) or rev_liked_in_redis
                rev.has_liked = rev_has_liked


