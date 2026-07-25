from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from user.db.models import User
from notification.db.models import Notification, PartnerType
from notification.services.notification import NotificationService, process_notifications


class NotificationStrategyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
        )

    def test_milestones_trigger_notification(self):
        now = timezone.now()
        milestones = [1, 100, 1000, 10000]
        for likes in milestones:
            self.assertTrue(
                NotificationService.should_send_notification(likes, now, now)
            )

    def test_multiples_of_100k_trigger_notification(self):
        now = timezone.now()
        self.assertTrue(
            NotificationService.should_send_notification(100000, now, now)
        )
        self.assertTrue(
            NotificationService.should_send_notification(200000, now, now)
        )
        self.assertFalse(
            NotificationService.should_send_notification(150000, now, now)
        )

    def test_throttling_intervals(self):
        now = timezone.now()

        # 1-10 likes: > 1 hour
        recent_30m = now - timedelta(minutes=30)
        old_2h = now - timedelta(hours=2)
        self.assertFalse(
            NotificationService.should_send_notification(5, now, recent_30m)
        )
        self.assertTrue(
            NotificationService.should_send_notification(5, now, old_2h)
        )

        # 10-100 likes: > 10 hours
        recent_5h = now - timedelta(hours=5)
        old_12h = now - timedelta(hours=12)
        self.assertFalse(
            NotificationService.should_send_notification(50, now, recent_5h)
        )
        self.assertTrue(
            NotificationService.should_send_notification(50, now, old_12h)
        )

        # 100-1000 likes: > 2 days
        recent_1d = now - timedelta(days=1)
        old_3d = now - timedelta(days=3)
        self.assertFalse(
            NotificationService.should_send_notification(500, now, recent_1d)
        )
        self.assertTrue(
            NotificationService.should_send_notification(500, now, old_3d)
        )

        # 1000-10000 likes: > 4 days
        recent_3d = now - timedelta(days=3)
        old_5d = now - timedelta(days=5)
        self.assertFalse(
            NotificationService.should_send_notification(5000, now, recent_3d)
        )
        self.assertTrue(
            NotificationService.should_send_notification(5000, now, old_5d)
        )

        # 10000-100000 likes: > 10 days
        recent_8d = now - timedelta(days=8)
        old_12d = now - timedelta(days=12)
        self.assertFalse(
            NotificationService.should_send_notification(50000, now, recent_8d)
        )
        self.assertTrue(
            NotificationService.should_send_notification(50000, now, old_12d)
        )

    def test_process_notifications(self):
        items = [
            {
                'user_id': self.user.id,
                'partner_id': 101,
                'total_likes': 1,
            }
        ]
        created = process_notifications(items, PartnerType.POST, 'like')
        self.assertEqual(len(created), 1)
        self.assertEqual(Notification.objects.count(), 1)
        notif = Notification.objects.first()
        self.assertEqual(notif.user_id, self.user.id)
        self.assertEqual(notif.partner_id, 101)
        self.assertEqual(notif.partner_type, PartnerType.POST)
