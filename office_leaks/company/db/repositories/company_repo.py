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
    def get_companies(page=1, page_size=10):
        try:
            queryset = Company.objects.all()
            total = queryset.count() if page == 1 else None
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "total": total or 0,
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
