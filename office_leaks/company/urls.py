from django.urls import path
from .views import company_views
from .views import rate_views

urlpatterns = [
    path('create/', company_views.create_company, name='create-company'),
    path('update/<int:company_id>/', company_views.update_company, name='update-company'),
    path('delete/<int:company_id>/', company_views.delete_company, name='delete-company'),
    path('', company_views.get_companies, name='get-companies'),
    path('rate/create/', rate_views.create_company_rate, name='create-company-rate'),
    path('rate/', rate_views.get_company_rate, name='get-company-rate'),
]