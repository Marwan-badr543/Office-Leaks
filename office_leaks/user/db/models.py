from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    # AbstractUser provides: username, password, first_name, last_name, is_staff, is_active, date_joined, etc.
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    
    age = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150),
        ])

    about = models.TextField(max_length=1000, blank=True, null=True)
    profile_image = models.ImageField(blank=True, null=True)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50)
    user_timezone = models.CharField(default='Africa/Cairo', max_length=50, blank=True, null=True)

    REQUIRED_FIELDS = ["age", "country", "first_name", "last_name"]

    def __str__(self):
        return self.username
