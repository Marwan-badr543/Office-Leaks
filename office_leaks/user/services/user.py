from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from user.db.repositories.user_repo import UserRepo
from core.exceptions import ValidationError


class UserServices():

    @staticmethod
    def create_user(validated_data):
        username = validated_data.get('username')
        if UserRepo.get_user_by_username(username):
            raise ValidationError("Username already exists.")

        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        
        with transaction.atomic():
            return UserRepo.create_user(validated_data)


    @staticmethod
    def login(validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')

        user = authenticate(username=username, password=password)
        
        if not user or not user.is_active:
            raise ValidationError("Invalice credentials")

        refresh = RefreshToken.for_user(user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

