from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)  # Indica si el usuario es profesor
    is_student = models.BooleanField(default=True)  # Indica si el usuario es estudiante

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

    def __str__(self):
        return self.username
