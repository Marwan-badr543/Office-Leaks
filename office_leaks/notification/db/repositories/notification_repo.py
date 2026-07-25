from notification.db.models import Notification
from core.exceptions import DatabaseError


class NotificationRepo():

    @staticmethod
    def create_notification(notification_data: dict):
        try:
            return Notification.objects.create(**notification_data)
        except Exception as e:
            raise DatabaseError(f"DatabaseError in create_notification: {e}")

    @staticmethod
    def get_last_notification(user_id: int, partner_id: int, partner_type: str):
        try:
            return Notification.objects.filter(
                user_id=user_id,
                partner_id=partner_id,
                partner_type=partner_type,
            ).order_by('-creation').first()
        except Exception as e:
            raise DatabaseError(f"DatabaseError in get_last_notification: {e}")
