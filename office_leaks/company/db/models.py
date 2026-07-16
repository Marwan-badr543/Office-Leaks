from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Company(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    industry = models.CharField(max_length=50)
    logo = models.CharField(blank=True, null=True)
    founded_at = models.DateField(blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    current_rate = models.FloatField(default=0)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='companies',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'industry'], name='unique_company_name_industry')
        ]

    def __str__(self):
        return self.name


class CompanyRate(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='company_rates',
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='rates',
    )
    
    rate = models.FloatField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'company'], name='unique_user_company_rate')
        ]
    
    def __str__(self):
        return f'{self.user.username} rated {self.company.name}: {self.rate}'