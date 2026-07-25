import logging
from collections import Counter
from django.db import transaction
from core.redis_client import get_redis_client
from review.db.models import PostLike
from review.db.repositories.post_like_repo import PostLikeRepo
from review.db.repositories.post_repo import PostRepo
from review.tasks import flush_post_likes_task
from core.exceptions import DuplicateResourceError

logger = logging.getLogger(__name__)

REDIS_POST_LIKES_KEY = "global_post_likes_buffer"
BUFFER_MAX_SIZE = 100

ADD_LIKE_SCRIPT = """
local added = redis.call('SADD', KEYS[1], ARGV[1])
local total_count = redis.call('SCARD', KEYS[1])
return {added, total_count}
"""

REMOVE_LIKE_SCRIPT = """
local removed = redis.call('SREM', KEYS[1], ARGV[1])
local total_count = redis.call('SCARD', KEYS[1])

if total_count == 0 then
    redis.call('DEL', KEYS[1])
end

return {removed, total_count}
"""

FLUSH_LIKE_SCRIPT = """
local elements = redis.call('SMEMBERS', KEYS[1])
redis.call('DEL', KEYS[1])
return elements
"""


class PostLikeServices:

    @staticmethod
    def create_like(validated_data):
        user_id = validated_data.get('user_id')
        post_id = validated_data.get('post_id')

        r = get_redis_client()
        element = f"{user_id}:{post_id}"

        added, total_count = r.eval(
            ADD_LIKE_SCRIPT, 1, REDIS_POST_LIKES_KEY, element
        )

        if not added:
            raise DuplicateResourceError("You have already liked this post.")

        logger.info(
            f"Atomic ADD '{element}' to global Redis buffer. "
            f"Total system likes count: {total_count}/{BUFFER_MAX_SIZE}"
        )

        task_enqueued = False
        if total_count >= BUFFER_MAX_SIZE:
            flush_post_likes_task()
            task_enqueued = True

        return {
            "status": "success",
            "message": f"Like for post {post_id} by user {user_id} saved to global Redis buffer.",
            "user_id": user_id,
            "post_id": post_id,
            "added": bool(added),
            "total_system_buffer_count": total_count,
            "flush_task_enqueued": task_enqueued
        }

    @staticmethod
    def delete_like(user_id, post_id):
        r = get_redis_client()
        element = f"{user_id}:{post_id}"

        removed, total_count = r.eval(
            REMOVE_LIKE_SCRIPT, 1, REDIS_POST_LIKES_KEY, element
        )

        logger.info(
            f"Atomic SREM '{element}' from global Redis buffer. "
            f"Total system likes count: {total_count}/{BUFFER_MAX_SIZE}"
        )

        db_removed = False
        if not removed:
            like = PostLikeRepo.get_like_by_user_and_post(user_id, post_id)
            if like:
                with transaction.atomic():
                    PostLikeRepo.delete_like(like)
                    PostRepo.decrement_likes_count(post_id)
                db_removed = True

        return {
            "status": "success",
            "message": f"Like for post {post_id} by user {user_id} removed.",
            "user_id": user_id,
            "post_id": post_id,
            "removed": bool(removed) or db_removed,
            "total_system_buffer_count": total_count
        }

    @staticmethod
    def flush_likes_to_db():
        r = get_redis_client()
        elements = r.eval(FLUSH_LIKE_SCRIPT, 1, REDIS_POST_LIKES_KEY)

        if not elements:
            return 0

        likes_to_create = []
        post_like_counts = Counter()

        for item in elements:
            try:
                user_id_str, post_id_str = item.split(":")
                user_id = int(user_id_str)
                post_id = int(post_id_str)

                likes_to_create.append(
                    PostLike(user_id=user_id, post_id=post_id)
                )
                post_like_counts[post_id] += 1
            except (ValueError, AttributeError):
                continue

        if not likes_to_create:
            return 0

        with transaction.atomic():
            PostLikeRepo.bulk_create_likes(likes_to_create)

            for post_id, count in post_like_counts.items():
                PostRepo.increment_likes_count(post_id, count=count)

        logger.info(f"Flushed {len(likes_to_create)} likes from Redis buffer into DB.")
        return len(likes_to_create)
