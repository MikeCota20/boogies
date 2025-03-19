from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)  # Agregar el campo is_teacher

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True
    )
