from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    upi_id = models.CharField(
        "UPI ID / payment handle",
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. yourname@upi — shown to others so they know where to pay you back.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.get_full_name() or self.username

    def display_name(self):
        return self.full_name or self.get_full_name() or self.username