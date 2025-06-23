from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPES = (
        ("applicant", "Job Applicant"),
        ("hr", "HR Manager"),
        ("admin", "System Administrator"),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default="applicant")
    phone = models.CharField(max_length=15, blank=True)
    company_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ApplicantProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="applicant_profile")
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.user.email}"


class HRProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="hr_profile")
    company_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company_name}"
