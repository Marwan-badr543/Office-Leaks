from company.db.models import CompanyRate
from django.db.models import Sum, Count
from core.exceptions import DatabaseError


class CompanyRateRepo():

    @staticmethod
    def create_company_rate(rate_data: dict):
        try:
            return CompanyRate.objects.create(**rate_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_company_rate: {e}")

    @staticmethod
    def has_user_rated_company(user_id, company_id):
        try:
            return CompanyRate.objects.filter(user_id=user_id, company_id=company_id).exists()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in has_user_rated_company: {e}")

    @staticmethod
    def get_company_rate_stats(company_id):
        try:
            return CompanyRate.objects.filter(company_id=company_id).aggregate(
                total=Sum("rate"),
                count=Count("id")
            )
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_rates_for_company: {e}")

    @staticmethod
    def get_company_rate(user_id, company_id):
        try:
            return CompanyRate.objects.filter(user_id=user_id, company_id=company_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_company_rate: {e}")

    @staticmethod
    def update_company_rate(company_rate_obj: CompanyRate, rate_value: float):
        try:
            company_rate_obj.rate = rate_value
            company_rate_obj.save()
            return company_rate_obj
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_company_rate: {e}")

