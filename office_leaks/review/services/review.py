from django.db import transaction
from django.contrib.auth import get_user_model
from review.db.repositories.review_repo import ReviewRepo
from company.db.repositories.company_repo import CompanyRepo
from core.exceptions import NotFoundError, ValidationError


User = get_user_model()


class ReviewServices():

    @staticmethod
    def validate_user_and_company_exist(user_id, company_id):
        if not CompanyRepo.get_company_with_id(company_id):
            raise NotFoundError(f"Company with id {company_id} not found.")

        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")

    @staticmethod
    def create_review(validated_data):
        user_id = validated_data.get('user_id')
        company_id = validated_data.get('company_id')

        ReviewServices.validate_user_and_company_exist(user_id, company_id)

        with transaction.atomic():
            review = ReviewRepo.create_review(validated_data)
            review.has_liked = False
            return review

    @staticmethod
    def update_review(review_id, user_id, validated_data):
        review = ReviewRepo.get_review_by_id(review_id)
        if not review:
            raise NotFoundError(f"Review with id {review_id} not found.")

        if review.user_id != user_id:
            raise ValidationError("You can only update your own reviews.")

        with transaction.atomic():
            ReviewRepo.update_review(review_id, validated_data)
            return ReviewServices.get_review_by_id(review_id)

    @staticmethod
    def get_reviews_by_company(company_id, page, page_size, user=None):
        if not CompanyRepo.get_company_with_id(company_id):
            raise NotFoundError(f"Company with id {company_id} not found.")

        result = ReviewRepo.get_reviews_by_company(company_id, page, page_size)
        reviews = result.get("reviews", [])

        if reviews:
            review_ids = [r.id for r in reviews]

            # Fetch likes from Redis buffer to adjust likes counts
            from collections import Counter
            from core.redis_client import get_redis_client
            redis_likes_count = Counter()
            try:
                r = get_redis_client()
                members = r.smembers("global_review_likes_buffer")
                if members:
                    for m in members:
                        try:
                            item_str = m if isinstance(m, str) else m.decode()
                            _, r_id_str = item_str.split(':')
                            redis_likes_count[int(r_id_str)] += 1
                        except Exception:
                            continue
            except Exception:
                pass

            # Check which reviews the user has liked
            liked_review_ids = set()
            if user and user.is_authenticated:
                from review.db.repositories.review_like_repo import ReviewLikeRepo
                liked_in_db = ReviewLikeRepo.get_liked_review_ids_by_user(user.id, review_ids)

                liked_in_redis = set()
                try:
                    r = get_redis_client()
                    pipe = r.pipeline()
                    for r_id in review_ids:
                        pipe.sismember("global_review_likes_buffer", f"{user.id}:{r_id}")
                    results = pipe.execute()
                    for r_id, is_member in zip(review_ids, results):
                        if is_member:
                            liked_in_redis.add(r_id)
                except Exception:
                    pass

                liked_review_ids = liked_in_db.union(liked_in_redis)

            for r in reviews:
                r.likes_number += redis_likes_count.get(r.id, 0)
                r.has_liked = r.id in liked_review_ids

        return result

    @staticmethod
    def get_review_by_id(review_id, user=None):
        review = ReviewRepo.get_review_by_id(review_id)
        if not review:
            raise NotFoundError(f"Review with id {review_id} not found.")

        # Adjust likes count for pending likes in Redis buffer
        from core.redis_client import get_redis_client
        redis_likes = 0
        try:
            r = get_redis_client()
            members = r.smembers("global_review_likes_buffer")
            if members:
                for m in members:
                    try:
                        item_str = m if isinstance(m, str) else m.decode()
                        _, r_id_str = item_str.split(':')
                        if int(r_id_str) == review.id:
                            redis_likes += 1
                    except Exception:
                        continue
        except Exception:
            pass
        review.likes_number += redis_likes

        # Check if user liked it
        has_liked = False
        if user and user.is_authenticated:
            from review.db.repositories.review_like_repo import ReviewLikeRepo
            liked_in_db = ReviewLikeRepo.get_liked_review_ids_by_user(user.id, [review.id])
            liked_in_redis = False
            try:
                r = get_redis_client()
                liked_in_redis = bool(r.sismember("global_review_likes_buffer", f"{user.id}:{review.id}"))
            except Exception:
                pass
            has_liked = (review.id in liked_in_db) or liked_in_redis
        
        review.has_liked = has_liked
        return review

    @staticmethod
    def delete_review(review_id, user_id):
        review = ReviewRepo.get_review_by_id(review_id)
        if not review:
            raise NotFoundError(f"Review with id {review_id} not found.")

        if review.user_id != user_id:
            raise ValidationError("You can only delete your own reviews.")

        with transaction.atomic():
            ReviewRepo.delete_review(review)
            return review
