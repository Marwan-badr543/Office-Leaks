from django.urls import path
from .views import user as user_views

urlpatterns = [
    path('create/', user_views.create_user, name='create-user'),
    path('login/', user_views.login, name='login'),
    path('token/refresh/', user_views.refresh_token, name='token-refresh'),
    path('upload-profile-image/', user_views.upload_profile_image, name='upload-profile-image'),
    path('delete-profile-image/', user_views.delete_profile_image, name='delete-profile-image'),
    path('update/', user_views.update_user, name='update-user'),
    path('change-password/', user_views.change_password, name='change-password'),
    path('delete/', user_views.delete_user, name='delete-user'),
    path('<int:user_id>/', user_views.get_user_by_id, name='get-user-by-id'),
    path('', user_views.get_users_by_full_name, name='get-users-by-full-name'),
]
