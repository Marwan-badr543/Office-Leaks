import logging
import json
from huey.contrib.djhuey import task, periodic_task
from huey import crontab
from core.redis_client import get_redis_client


logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Post Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_post_likes_task():
    from review.services.post_like import PostLikeServices
    flushed_count = PostLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} post likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_post_likes_task():
    from review.services.post_like import PostLikeServices
    flushed_count = PostLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} post likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Review Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_review_likes_task():
    from review.services.review_like import ReviewLikeServices
    flushed_count = ReviewLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} review likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_review_likes_task():
    from review.services.review_like import ReviewLikeServices
    flushed_count = ReviewLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} review likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Review Comment Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_review_comment_likes_task():
    from review.services.review_comment_like import ReviewCommentLikeServices
    flushed_count = ReviewCommentLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} review comment likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_review_comment_likes_task():
    from review.services.review_comment_like import ReviewCommentLikeServices
    flushed_count = ReviewCommentLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} review comment likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Review Nested Comment Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_review_nested_comment_likes_task():
    from review.services.review_nested_comment_like import ReviewNestedCommentLikeServices
    flushed_count = ReviewNestedCommentLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} review nested comment likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_review_nested_comment_likes_task():
    from review.services.review_nested_comment_like import ReviewNestedCommentLikeServices
    flushed_count = ReviewNestedCommentLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} review nested comment likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Post Comment Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_post_comment_likes_task():
    from review.services.post_comment_like import PostCommentLikeServices
    flushed_count = PostCommentLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} post comment likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_post_comment_likes_task():
    from review.services.post_comment_like import PostCommentLikeServices
    flushed_count = PostCommentLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} post comment likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Post Nested Comment Likes Tasks
# ------------------------------------------------------------------

@task()
def flush_post_nested_comment_likes_task():
    from review.services.post_nested_comment_like import PostNestedCommentLikeServices
    flushed_count = PostNestedCommentLikeServices.flush_likes_to_db()
    logger.info(f"Huey task flushed {flushed_count} post nested comment likes into DB.")
    return flushed_count


@periodic_task(crontab(minute='*'))
def periodic_flush_post_nested_comment_likes_task():
    from review.services.post_nested_comment_like import PostNestedCommentLikeServices
    flushed_count = PostNestedCommentLikeServices.flush_likes_to_db()
    if flushed_count > 0:
        logger.info(f"Huey periodic task flushed {flushed_count} post nested comment likes into DB.")
    return flushed_count


# ------------------------------------------------------------------
# Trending Topics Tasks
# ------------------------------------------------------------------

REDIS_KEY_TRENDING_CATEGORIES = "post:trending_categories"

@periodic_task(crontab(hour='*/12', minute='0'))
def update_trending_categories_task():
    """
    Periodic task that runs every 12 hours.
    Retrieves the top 6 trending post categories from the past week
    and caches them in Redis with a 13-hour TTL.
    """
    logger.info("Starting update_trending_categories_task...")
    try:
        # Lazy import of Service layer to avoid circular dependencies during worker startup
        from review.services.post import PostServices
        
        # Query top 6 trending categories
        trending = PostServices.get_trending_categories(limit=6)
        
        # Serialize the category list using list comprehension
        trending_list = [
            {
                "category": item["category"],
                "count": item["count"]
            }
            for item in trending
        ]
        
        if trending_list:
            r = get_redis_client()
            
            # Put new trending data directly (implicit overwrite prevents race conditions)
            serialized_data = json.dumps(trending_list)
            r.set(REDIS_KEY_TRENDING_CATEGORIES, serialized_data, ex=13 * 3600)
            
            logger.info(f"Successfully updated trending categories in Redis: {len(trending_list)} categories cached under key '{REDIS_KEY_TRENDING_CATEGORIES}'.")
            return len(trending_list)
        return 0
    except Exception as e:
        logger.error(f"Error updating trending categories in Redis: {e}", exc_info=True)
        raise

