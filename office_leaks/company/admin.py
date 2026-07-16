from django.contrib import admin
from .db.models import Company, CompanyRate


admin.site.register(Company)
admin.site.register(CompanyRate)