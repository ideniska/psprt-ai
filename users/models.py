from typing import TypeVar
from django.contrib.auth.models import AbstractUser
from django.core import signing
from django.db import models
from .managers import UserManager
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

UserType = TypeVar("UserType", bound="User")


class User(AbstractUser):
    # username = None  # type: ignore
    email = models.EmailField("Email address", unique=True)
    is_demo = models.BooleanField(default=False)
    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
