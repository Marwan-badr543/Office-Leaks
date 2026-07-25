from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from user.db.repositories.user_repo import UserRepo
from core.exceptions import ValidationError, NotFoundError
from core.storage import R2StorageService


class UserServices():

    @staticmethod
    def create_user(validated_data):
        username = validated_data.get('username')
        if UserRepo.get_user_by_username(username):
            raise ValidationError("Username already exists.")

        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        
        # Concatenate first_name and last_name to full_name
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        validated_data['full_name'] = f"{first_name} {last_name}".strip()

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

    @staticmethod
    def refresh_token(refresh_token_str):
        if not refresh_token_str:
            raise ValidationError("Refresh token is missing")
        try:
            refresh = RefreshToken(refresh_token_str)
            data = {
                'access': str(refresh.access_token),
            }
            # Handle token rotation if configured
            from django.conf import settings
            if getattr(settings, 'SIMPLE_JWT', {}).get('ROTATE_REFRESH_TOKENS', False):
                refresh.set_jti()
                refresh.set_exp()
                data['refresh'] = str(refresh)
            return data
        except Exception:
            raise ValidationError("Token is invalid or expired")

    @staticmethod
    def upload_profile_image(user, image_file):
        """
        Upload a profile image to R2 and store the UUID filename in the DB.

        If the user already has a profile image, the old one is deleted from R2
        first to prevent orphaned files accumulating in storage.

        Flow:
        1. Delete old image from R2 (if exists) — idempotent, won't fail if missing
        2. Upload new image to R2 — validates type, magic bytes, and size
        3. Update the DB field with the new UUID filename

        Why not wrap in transaction.atomic()? The R2 upload is an external HTTP call.
        If the DB update fails after a successful R2 upload, we'd have an orphan in R2,
        but that's preferable to wrapping an external call inside a DB transaction
        (which would hold the connection open during the upload).
        """
        old_filename = user.profile_image

        # Upload new image first — if validation or upload fails, we haven't touched anything
        new_filename = R2StorageService.upload_image(image_file)

        # Update DB
        UserRepo.update_profile_image(user.id, new_filename)

        # Delete old image from R2 AFTER successful DB update
        # This order ensures we never lose the reference to the new image
        if old_filename:
            R2StorageService.delete_image(old_filename)

        return new_filename

    @staticmethod
    def delete_profile_image(user):
        """
        Remove the user's profile image from both R2 and the database.

        Idempotent — if the user has no profile image, this is a no-op.
        """
        filename = user.profile_image
        if not filename:
            raise ValidationError("No profile image to delete.")

        # Clear DB first, then delete from R2.
        # If R2 delete fails, we only have an orphaned file (minor cost)
        # rather than a DB pointing to a deleted file (broken reference).
        UserRepo.update_profile_image(user.id, None)
        R2StorageService.delete_image(filename)

    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepo.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found.")
        return user


    @staticmethod
    def get_users(page, page_size, filters=None):
        return UserRepo.get_users(page, page_size, filters)

    @staticmethod
    def update_user(user_id: int, update_data: dict):
        """
        Partial update of user profile fields.
        Username (email) is explicitly excluded from updates.
        """
        user = UserRepo.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found.")

        # Never allow username change
        update_data.pop('username', None)
        update_data.pop('password', None)

        if not update_data:
            raise ValidationError("No valid fields to update.")

        with transaction.atomic():
            return UserRepo.update_user(user_id, update_data)

    @staticmethod
    def change_password(user, old_password: str, new_password: str):
        """
        Verify old password and set new password for the authenticated user.
        """
        if not check_password(old_password, user.password):
            raise ValidationError("Current password is incorrect.")

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return user

    @staticmethod
    def delete_user(user):
        """
        Hard-delete a user account. This is irreversible.
        """
        user_id = user.id
        with transaction.atomic():
            deleted_user = UserRepo.delete_user(user_id)
            if not deleted_user:
                raise NotFoundError(f"User with id {user_id} not found.")
        return deleted_user
