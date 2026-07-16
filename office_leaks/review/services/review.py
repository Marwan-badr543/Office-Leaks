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
            return ReviewRepo.create_review(validated_data)

    @staticmethod
    def update_review(review_id, user_id, validated_data):
        review = ReviewRepo.get_review_by_id(review_id)
        if not review:
            raise NotFoundError(f"Review with id {review_id} not found.")

        if review.user_id != user_id:
            raise ValidationError("You can only update your own reviews.")

        with transaction.atomic():
            ReviewRepo.update_review(review_id, validated_data)
            return ReviewRepo.get_review_by_id(review_id)

    @staticmethod
    def get_reviews_by_company(company_id, page, page_size):
        if not CompanyRepo.get_company_with_id(company_id):
            raise NotFoundError(f"Company with id {company_id} not found.")

        return ReviewRepo.get_reviews_by_company(company_id, page, page_size)

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
