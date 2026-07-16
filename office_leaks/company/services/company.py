from ..db.repositories.company_repo import CompanyRepo
from django.db import transaction
from core.exceptions import NotFoundError

class CompanyServices():

    @staticmethod
    def create_company(validated_data):
        with transaction.atomic():
            return CompanyRepo.create_company(validated_data)

    @staticmethod
    def update_company(cmpny_id, cmpny_data):
        if not CompanyRepo.get_company_with_id(cmpny_id):
            raise NotFoundError(f"Company with id {cmpny_id} not found.")

        with transaction.atomic():
            return CompanyRepo.update_company(cmpny_id, cmpny_data)


    @staticmethod
    def delete_company(cmpny_id):
        company = CompanyRepo.get_company_with_id(cmpny_id)
        if not company:
            raise NotFoundError(f"Company with id {cmpny_id} not found.")
        
        with transaction.atomic():
            CompanyRepo.delete_company(company)
            return company


    @staticmethod
    def get_companies(page, page_size):
        return CompanyRepo.get_companies(page, page_size)