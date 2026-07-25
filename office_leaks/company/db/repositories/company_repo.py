from typing import Optional
from django.db.models import Q
from company.db.models import Company
from core.exceptions import DatabaseError


class CompanyRepo():

    @staticmethod
    def create_company(cmpny_data:dict):
        try:
            return Company.objects.create(**cmpny_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_company: {e}")

    @staticmethod
    def get_company_by_name_exact(name: str) -> Optional[Company]:
        try:
            return Company.objects.filter(name__iexact=name).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_company_by_name_exact: {e}")

    @staticmethod
    def update_company(cmpny_id, cmpny_data:dict):
        try:
            return Company.objects.filter(id=cmpny_id).update(**cmpny_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_company: {e}")


    @staticmethod
    def get_company_with_id(cmpny_id):
        try:
            return Company.objects.filter(id=cmpny_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_company_with_id: {e}")


    @staticmethod
    def delete_company(cmpny_obj:Company):
        try:
            cmpny_obj.delete()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_company: {e}")


    @staticmethod
    def get_companies(page=1, page_size=10, filters=None):
        try:
            q = Q()
            if filters:
                if filters.get('name_search'):
                    q &= Q(name__icontains=filters['name_search'])
                if filters.get('industry'):
                    q &= Q(industry=filters['industry'])
                min_rate = filters.get('min_rate')
                max_rate = filters.get('max_rate')
                if min_rate is not None and max_rate is not None:
                    q &= Q(current_rate__range=(min_rate, max_rate))
                elif min_rate is not None:
                    q &= Q(current_rate__gte=min_rate)
                elif max_rate is not None:
                    q &= Q(current_rate__lte=max_rate)

            queryset = Company.objects.filter(q).order_by('-current_rate')
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "companies": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_companies: {e}")

    @staticmethod
    def update_company_rating(company_id, current_rate):
        try:
            Company.objects.filter(id=company_id).update(current_rate=current_rate)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_company_rating: {e}")

    @staticmethod
    def update_company_logo(company_id, filename):
        """
        Set the logo field to the given UUID filename.
        Uses filter().update() for a single UPDATE query without loading the object.
        """
        try:
            return Company.objects.filter(id=company_id).update(logo=filename)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_company_logo: {e}")

    @staticmethod
    def get_top_rated_companies(limit=10):
        try:
            return Company.objects.order_by('-current_rate')[:limit]
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_top_rated_companies: {e}")

    @staticmethod
    def search_companies_by_name(name_search: str, limit: int = 10):
        try:
            return Company.objects.filter(name__icontains=name_search).order_by('-current_rate')[:limit]
        except Exception as e:
            raise DatabaseError(f"DatabaseError in search_companies_by_name: {e}")



