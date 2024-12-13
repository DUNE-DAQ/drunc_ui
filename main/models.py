"""Models module for the main app."""

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for this project."""

    class Meta:
        """Meta class for the User model."""

        permissions: ClassVar = [
            ("can_modify_processes", "Can modify processes"),
            ("can_view_process_logs", "Can view process logs"),
        ]


class DruncMessage(models.Model):
    """Model for drunc broadcast messages."""

    SEVERITY_CHOICES = (
        ("INFO", "INFO"),
        ("CRITICAL", "CRITICAL"),
        ("ERROR", "ERROR"),
        ("DEBUG", "DEBUG"),
    )

    topic = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="INFO")
