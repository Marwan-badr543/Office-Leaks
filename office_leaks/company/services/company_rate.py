from django.db import transaction
from django.contrib.auth import get_user_model
from company.db.repositories.company_rete_repo import CompanyRateRepo
from company.db.repositories.company_repo import CompanyRepo
from core.exceptions import NotFoundError, DuplicateResourceError


User = get_user_model()

class CompanyRateServices():

    @staticmethod
    def validate_user_and_company_exist(user_id, company_id):
        # Check if company exists
        if not CompanyRepo.get_company_with_id(company_id):
            raise NotFoundError(f"Company with id {company_id} not found.")

        # Check if user exists
        if not User.objects.filter(id=user_id).exists():
            raise NotFoundError(f"User with id {user_id} not found.")
            

    @staticmethod
    def update_company_rating(company_id):
        # 1. Fetch the sum of rates and counts from the DB repository
        stats = CompanyRateRepo.get_company_rate_stats(company_id)

        total = stats.get("total") or 0.0
        count = stats.get("count") or 0

        # 2. Compute the average rating
        if count == 0:
            avg_rating = 0.0
        else:
            avg_rating = total / count

        # 3. Save the new rating to the Company model in the DB
        CompanyRepo.update_company_rating(company_id, avg_rating)


    @staticmethod
    def update_or_create_company_rate(validated_data):
        company_id = validated_data.get('company_id')
        user_id = validated_data.get('user_id')
        rate_value = validated_data.get('rate')

        CompanyRateServices.validate_user_and_company_exist(user_id, company_id)

        # Get existing rate if any
        existing_rate = CompanyRateRepo.get_company_rate(user_id, company_id)

        with transaction.atomic():
            if existing_rate:
                # Update existing rate
                rate = CompanyRateRepo.update_company_rate(existing_rate, rate_value)
                CompanyRateServices.update_company_rating(company_id)
                return rate, False  # False means updated
            else:
                # Create new rate
                rate = CompanyRateRepo.create_company_rate(validated_data)
                CompanyRateServices.update_company_rating(company_id)
                return rate, True   # True means created


    @staticmethod
    def get_company_rate(user_id, company_id):
        CompanyRateServices.validate_user_and_company_exist(user_id, company_id)

        rate = CompanyRateRepo.get_company_rate(user_id, company_id)
        if not rate:
            raise NotFoundError(f"Rate for user {user_id} and company {company_id} not found.")
        return rate

