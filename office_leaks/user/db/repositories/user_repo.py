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
