from django.db.models import Q
from user.db.models import User
from core.exceptions import DatabaseError


class UserRepo():

    @staticmethod
    def create_user(user_data: dict):
        try:
            return User.objects.create(**user_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_user: {e}")

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.filter(id=user_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_user_by_id: {e}")

    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.filter(username=username).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_user_by_username: {e}")

    @staticmethod
    def update_profile_image(user_id, filename):
        """
        Set the profile_image field to the given UUID filename.
        Uses filter().update() for a single UPDATE query without loading the object.
        """
        try:
            return User.objects.filter(id=user_id).update(profile_image=filename)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_profile_image: {e}")

    @staticmethod
    def update_user(user_id: int, update_data: dict):
        """
        Partial update of user fields. Uses filter().update() for efficiency.
        Returns the updated User object.
        """
        try:
            # Build full_name if first or last name changed
            if 'first_name' in update_data or 'last_name' in update_data:
                user = User.objects.filter(id=user_id).first()
                if user:
                    first = update_data.get('first_name', user.first_name)
                    last = update_data.get('last_name', user.last_name)
                    update_data['full_name'] = f"{first} {last}".strip()

            User.objects.filter(id=user_id).update(**update_data)
            return User.objects.filter(id=user_id).first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in update_user: {e}")

    @staticmethod
    def delete_user(user_id: int):
        """Hard-delete a user by ID."""
        try:
            user = User.objects.filter(id=user_id).first()
            if user:
                user.delete()
            return user
        except Exception as e:
            raise DatabaseError(f"DatabaseError in delete_user: {e}")

    @staticmethod
    def get_users(page=1, page_size=10, filters=None):
        try:
            q = Q()
            if filters and filters.get('full_name'):
                q &= Q(full_name__icontains=filters['full_name'])

            queryset = User.objects.filter(q).order_by('-date_joined')
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "users": queryset[start:end],
            }
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_users: {e}")
