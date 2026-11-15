from django.contrib.auth.models import User

from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [('student', 'Student'), ('alumni', 'Alumni')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_verified = models.BooleanField(default=False)

    batch_year = models.PositiveIntegerField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=255, blank=True,
                              help_text='Comma-separated, e.g. Python, SQL, ML')
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'
class MentorshipRequest(models.Model):
    STATUS = [("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    alumnus = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "alumnus")
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title