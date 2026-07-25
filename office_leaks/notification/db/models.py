from django.db import models
from django.utils import timezone

class PartnerType(models.TextChoices):
    POST = 'POST', 'Post'
    REVIEW = 'REVIEW', 'Review'
    COMPANY = 'COMPANY', 'Company'
    USER = 'USER', 'User'


class Notification(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    partner_id = models.BigIntegerField(null=True, blank=True)
    partner_type = models.CharField(
        max_length=50,
        choices=PartnerType.choices,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', '-creation'], name='notif_user_creation_idx'),
            models.Index(
                fields=['user', 'partner_id', 'partner_type', '-creation'],
                name='notif_partner_lookup_idx',
            ),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
