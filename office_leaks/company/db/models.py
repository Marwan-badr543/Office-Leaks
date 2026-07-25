from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .model_choices import CompanyIndustry


class Company(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    industry = models.CharField(
        max_length=100,
        choices=CompanyIndustry.choices,
        default=CompanyIndustry.OTHER,
    )
    logo = models.CharField(max_length=255, blank=True, null=True)
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
        indexes = [
            models.Index(fields=['industry'], name='company_industry_idx'),
            models.Index(fields=['-current_rate'], name='company_rate_idx'),
            # For Postgres: replace with GinIndex(fields=['name'], name='company_name_idx', opclasses=['gin_trgm_ops'])
            models.Index(fields=['name'], name='company_name_idx'),
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