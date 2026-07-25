from datetime import timedelta
from django.utils import timezone
from notification.db.repositories.notification_repo import NotificationRepo


class NotificationService:

    @staticmethod
    def should_send_notification(total_likes: int, now, last_creation) -> bool:
        if total_likes <= 0:
            return False

        if total_likes in (1, 100, 1000, 10000):
            return True

        if total_likes >= 100000:
            return total_likes % 100000 == 0

        if last_creation is None:
            return True

        time_diff = now - last_creation

        if 1 < total_likes < 10:
            return time_diff > timedelta(hours=1)
        elif 10 <= total_likes < 100:
            return time_diff > timedelta(hours=10)
        elif 100 < total_likes < 1000:
            return time_diff > timedelta(days=2)
        elif 1000 < total_likes < 10000:
            return time_diff > timedelta(days=4)
        elif 10000 < total_likes < 100000:
            return time_diff > timedelta(days=10)

        return False

    @staticmethod
    def process_notifications(
        items: list[dict],
        partner_type: str,
        notification_type: str,
    ) -> list:
        """
        Process a list of dicts containing user_id, partner_id, total_likes (or total_count).
        Checks strategy rules against last notification time and creates new notifications.
        """
        now = timezone.now()
        created_notifications = []

        for item in items:
            user_id = item.get('user_id')
            partner_id = item.get('partner_id')
            total_likes = item.get(
                'total_likes',
                item.get('total_count', item.get('count', item.get('likes_count', 0))),
            )

            if not user_id or not partner_id:
                continue

            last_notification = NotificationRepo.get_last_notification(
                user_id=user_id,
                partner_id=partner_id,
                partner_type=partner_type,
            )

            last_creation = last_notification.creation if last_notification else None

            if NotificationService.should_send_notification(total_likes, now, last_creation):
                message = (
                    f"Your {partner_type.lower()} has reached {total_likes} {notification_type}s."
                    if total_likes > 1
                    else f"Your {partner_type.lower()} received a new {notification_type}."
                )

                notification_data = {
                    'user_id': user_id,
                    'partner_id': partner_id,
                    'partner_type': partner_type,
                    'message': message,
                    'creation': now,
                }
                notification = NotificationRepo.create_notification(notification_data)
                created_notifications.append(notification)

        return created_notifications


def process_notifications(
    items: list[dict],
    partner_type: str,
    notification_type: str,
) -> list:
    """
    Module-level wrapper for NotificationService.process_notifications.
    """
    return NotificationService.process_notifications(items, partner_type, notification_type)
