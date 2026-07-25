from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.review_nested_comment_repo import ReviewNestedCommentRepo
from review.db.repositories.review_comment_repo import ReviewCommentRepo
from review.db.repositories.review_repo import ReviewRepo
from core.exceptions import NotFoundError, ValidationError

User = get_user_model()


class ReviewNestedCommentServices():

    @staticmethod
    def validate_user_and_parent_comment_exist(user_id, parent_comment_id):
        if not ReviewCommentRepo.get_comment_by_id(parent_comment_id):
            raise NotFoundError(f"Review comment with id {parent_comment_id} not found.")

        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

    @staticmethod
    def create_comment(validated_data):
        user_id = validated_data.get('user_id')
        parent_comment_id = validated_data.get('parent_comment_id')

        ReviewNestedCommentServices.validate_user_and_parent_comment_exist(user_id, parent_comment_id)

        parent_comment = ReviewCommentRepo.get_comment_by_id(parent_comment_id)
        validated_data['parent_comment_author_id'] = parent_comment.user_id

        review_id = parent_comment.review_id

        with transaction.atomic():
            comment = ReviewNestedCommentRepo.create_comment(validated_data)
            ReviewRepo.increment_comments_count(review_id)
            comment.has_liked = False
            return comment

    @staticmethod
    def update_comment(comment_id, user_id, validated_data, user=None):
        comment = ReviewNestedCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Nested comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only update your own comments.")

        with transaction.atomic():
            ReviewNestedCommentRepo.update_comment(comment_id, validated_data)
            return ReviewNestedCommentServices.get_comment_by_id(comment_id, user=user)

    @staticmethod
    def get_comment_by_id(comment_id, user=None):
        comment = ReviewNestedCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Nested comment with id {comment_id} not found.")
        
        # Adjust likes
        from core.redis_client import get_redis_client
        redis_likes = 0
        try:
            r = get_redis_client()
            members = r.smembers("global_review_nested_comment_likes_buffer")
            if members:
                for m in members:
                    try:
                        item_str = m if isinstance(m, str) else m.decode()
                        _, c_id_str = item_str.split(':')
                        if int(c_id_str) == comment.id:
                            redis_likes += 1
                    except Exception:
                        continue
        except Exception:
            pass
        comment.likes_number += redis_likes

        # Check liked
        has_liked = False
        if user and user.is_authenticated:
            from review.db.repositories.review_nested_comment_like_repo import ReviewNestedCommentLikeRepo
            liked_in_db = ReviewNestedCommentLikeRepo.get_liked_nested_comment_ids_by_user(user.id, [comment.id])
            liked_in_redis = False
            try:
                r = get_redis_client()
                liked_in_redis = bool(r.sismember("global_review_nested_comment_likes_buffer", f"{user.id}:{comment.id}"))
            except Exception:
                pass
            has_liked = (comment.id in liked_in_db) or liked_in_redis
        comment.has_liked = has_liked
        return comment

    @staticmethod
    def get_comments_by_parent(parent_comment_id, page, page_size, user=None):
        if not ReviewCommentRepo.get_comment_by_id(parent_comment_id):
            raise NotFoundError(f"Review comment with id {parent_comment_id} not found.")

        result = ReviewNestedCommentRepo.get_comments_by_parent(parent_comment_id, page, page_size)
        comments = result.get("comments", [])

        if comments:
            comment_ids = [c.id for c in comments]

            # Fetch pending likes from Redis buffer
            from collections import Counter
            from core.redis_client import get_redis_client
            redis_likes_count = Counter()
            try:
                r = get_redis_client()
                members = r.smembers("global_review_nested_comment_likes_buffer")
                if members:
                    for m in members:
                        try:
                            item_str = m if isinstance(m, str) else m.decode()
                            _, c_id_str = item_str.split(':')
                            redis_likes_count[int(c_id_str)] += 1
                        except Exception:
                            continue
            except Exception:
                pass

            # Fetch user liked nested comment IDs
            liked_comment_ids = set()
            if user and user.is_authenticated:
                from review.db.repositories.review_nested_comment_like_repo import ReviewNestedCommentLikeRepo
                liked_in_db = ReviewNestedCommentLikeRepo.get_liked_nested_comment_ids_by_user(user.id, comment_ids)

                liked_in_redis = set()
                try:
                    r = get_redis_client()
                    pipe = r.pipeline()
                    for c_id in comment_ids:
                        pipe.sismember("global_review_nested_comment_likes_buffer", f"{user.id}:{c_id}")
                    results = pipe.execute()
                    for c_id, is_member in zip(comment_ids, results):
                        if is_member:
                            liked_in_redis.add(c_id)
                except Exception:
                    pass

                liked_comment_ids = liked_in_db.union(liked_in_redis)

            for c in comments:
                c.likes_number += redis_likes_count.get(c.id, 0)
                c.has_liked = c.id in liked_comment_ids

        return result

    @staticmethod
    def delete_comment(comment_id, user_id):
        comment = ReviewNestedCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Nested comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only delete your own comments.")

        review_id = comment.parent_comment.review_id

        with transaction.atomic():
            ReviewNestedCommentRepo.delete_comment(comment)
            ReviewRepo.decrement_comments_count(review_id)
            return comment


