from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.post_comment_repo import PostCommentRepo
from review.db.repositories.post_repo import PostRepo
from core.exceptions import NotFoundError, ValidationError

User = get_user_model()


class PostCommentServices():

    @staticmethod
    def validate_user_and_post_exist(user_id, post_id):
        if not PostRepo.get_post_by_id(post_id):
            raise NotFoundError(f"Post with id {post_id} not found.")

        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

    @staticmethod
    def create_comment(validated_data):
        user_id = validated_data.get('user_id')
        post_id = validated_data.get('post_id')

        PostCommentServices.validate_user_and_post_exist(user_id, post_id)

        with transaction.atomic():
            comment = PostCommentRepo.create_comment(validated_data)
            PostRepo.increment_comments_count(post_id)
            PostRepo.increment_popularity_score(post_id, amount=2)
            comment.has_liked = False
            return comment

    @staticmethod
    def update_comment(comment_id, user_id, validated_data, user=None):
        comment = PostCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only update your own comments.")

        with transaction.atomic():
            PostCommentRepo.update_comment(comment_id, validated_data)
            return PostCommentServices.get_comment_by_id(comment_id, user=user)

    @staticmethod
    def get_comment_by_id(comment_id, user=None):
        comment = PostCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")
        
        # Adjust likes
        from core.redis_client import get_redis_client
        redis_likes = 0
        try:
            r = get_redis_client()
            members = r.smembers("global_post_comment_likes_buffer")
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
            from review.db.repositories.post_comment_like_repo import PostCommentLikeRepo
            liked_in_db = PostCommentLikeRepo.get_liked_comment_ids_by_user(user.id, [comment.id])
            liked_in_redis = False
            try:
                r = get_redis_client()
                liked_in_redis = bool(r.sismember("global_post_comment_likes_buffer", f"{user.id}:{comment.id}"))
            except Exception:
                pass
            has_liked = (comment.id in liked_in_db) or liked_in_redis
        comment.has_liked = has_liked
        return comment

    @staticmethod
    def get_comments_by_post(post_id, page, page_size, user=None):
        if not PostRepo.get_post_by_id(post_id):
            raise NotFoundError(f"Post with id {post_id} not found.")

        result = PostCommentRepo.get_comments_by_post(post_id, page, page_size)
        comments = result.get("comments", [])

        if comments:
            comment_ids = [c.id for c in comments]

            # Fetch pending likes from Redis buffer
            from collections import Counter
            from core.redis_client import get_redis_client
            redis_likes_count = Counter()
            try:
                r = get_redis_client()
                members = r.smembers("global_post_comment_likes_buffer")
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

            # Fetch user liked comment IDs
            liked_comment_ids = set()
            if user and user.is_authenticated:
                from review.db.repositories.post_comment_like_repo import PostCommentLikeRepo
                liked_in_db = PostCommentLikeRepo.get_liked_comment_ids_by_user(user.id, comment_ids)

                liked_in_redis = set()
                try:
                    r = get_redis_client()
                    pipe = r.pipeline()
                    for c_id in comment_ids:
                        pipe.sismember("global_post_comment_likes_buffer", f"{user.id}:{c_id}")
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
        comment = PostCommentRepo.get_comment_by_id(comment_id)
        if not comment:
            raise NotFoundError(f"Comment with id {comment_id} not found.")

        if comment.user_id != user_id:
            raise ValidationError("You can only delete your own comments.")

        post_id = comment.post_id

        with transaction.atomic():
            PostCommentRepo.delete_comment(comment)
            PostRepo.decrement_comments_count(post_id)
            PostRepo.decrement_popularity_score(post_id, amount=2)
            return comment
