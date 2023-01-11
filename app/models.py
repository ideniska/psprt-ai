import os
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import FileExtensionValidator
from users.models import CustomUser


DOCUMENT_TYPE_CHOICES = [
    ("australia_passport", "Australia Passport"),
    ("canada_passport", "Canada Passport"),
    ("canada_visa", "Canada Visa"),
    ("china_visa", "China Visa"),
    ("european_union_passport", "European Union Passport"),
    ("japan_visa", "Japan Visa"),
    ("india_visa", "India Visa"),
    ("schengen_visa", "Schengen Visa"),
    ("us_visa", "US Visa"),
    ("us_passport", "US Passport"),
]


def file_size(value):
    limit = 30 * 1024 * 1024
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 30 MB.")


class UserFile(models.Model):
    file = models.FileField(
        upload_to="",
        validators=[
            file_size,
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"]),
        ],
    )
    session = models.CharField(max_length=150)
    edited = models.BooleanField(default=False)
    prepared_for = models.CharField(choices=DOCUMENT_TYPE_CHOICES, max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
