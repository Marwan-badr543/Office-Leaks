from django.urls import path
from .views import user as user_views

urlpatterns = [
    path('create/', user_views.create_user, name='create-user'),
    path('login/', user_views.login, name='login'),
]
