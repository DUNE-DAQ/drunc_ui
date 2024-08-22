"""Models module for the main app."""

from django.contrib.auth.models import AbstractUser
from django.db import models  # noqa: F401


class User(AbstractUser):
    """Custom user model for this project."""
