import logging
from collections import Counter
from django.db import transaction
from core.redis_client import get_redis_client
from review.db.models import ReviewLike
from review.db.repositories.review_like_repo import ReviewLikeRepo
from review.db.repositories.review_repo import ReviewRepo
from review.tasks import flush_review_likes_task
from core.exceptions import DuplicateResourceError

logger = logging.getLogger(__name__)

REDIS_REVIEW_LIKES_KEY = "global_review_likes_buffer"
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


class ReviewLikeServices:

    @staticmethod
    def create_like(validated_data):
        user_id = validated_data.get('user_id')
        review_id = validated_data.get('review_id')

        r = get_redis_client()
        element = f"{user_id}:{review_id}"

        added, total_count = r.eval(
            ADD_LIKE_SCRIPT, 1, REDIS_REVIEW_LIKES_KEY, element
        )

        if not added:
            raise DuplicateResourceError("You have already liked this review.")

        logger.info(
            f"Atomic ADD '{element}' to global review likes Redis buffer. "
            f"Total system likes count: {total_count}/{BUFFER_MAX_SIZE}"
        )

        task_enqueued = False
        if total_count >= BUFFER_MAX_SIZE:
            flush_review_likes_task()
            task_enqueued = True

        return {
            "status": "success",
            "message": f"Like for review {review_id} by user {user_id} saved to global Redis buffer.",
            "user_id": user_id,
            "review_id": review_id,
            "added": bool(added),
            "total_system_buffer_count": total_count,
            "flush_task_enqueued": task_enqueued
        }

    @staticmethod
    def delete_like(user_id, review_id):
        r = get_redis_client()
        element = f"{user_id}:{review_id}"

        removed, total_count = r.eval(
            REMOVE_LIKE_SCRIPT, 1, REDIS_REVIEW_LIKES_KEY, element
        )

        logger.info(
            f"Atomic SREM '{element}' from global review likes Redis buffer. "
            f"Total system likes count: {total_count}/{BUFFER_MAX_SIZE}"
        )

        db_removed = False
        if not removed:
            like = ReviewLikeRepo.get_like_by_user_and_review(user_id, review_id)
            if like:
                with transaction.atomic():
                    ReviewLikeRepo.delete_like(like)
                    ReviewRepo.decrement_likes_count(review_id)
                db_removed = True

        return {
            "status": "success",
            "message": f"Like for review {review_id} by user {user_id} removed.",
            "user_id": user_id,
            "review_id": review_id,
            "removed": bool(removed) or db_removed,
            "total_system_buffer_count": total_count
        }

    @staticmethod
    def flush_likes_to_db():
        r = get_redis_client()
        elements = r.eval(FLUSH_LIKE_SCRIPT, 1, REDIS_REVIEW_LIKES_KEY)

        if not elements:
            return 0

        likes_to_create = []
        review_like_counts = Counter()

        for item in elements:
            try:
                user_id_str, review_id_str = item.split(":")
                user_id = int(user_id_str)
                review_id = int(review_id_str)

                likes_to_create.append(
                    ReviewLike(user_id=user_id, review_id=review_id)
                )
                review_like_counts[review_id] += 1
            except (ValueError, AttributeError):
                continue

        if not likes_to_create:
            return 0

        with transaction.atomic():
            ReviewLikeRepo.bulk_create_likes(likes_to_create)

            for review_id, count in review_like_counts.items():
                ReviewRepo.increment_likes_count(review_id, count=count)

        logger.info(f"Flushed {len(likes_to_create)} review likes from Redis buffer into DB.")
        return len(likes_to_create)
