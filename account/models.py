import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom User Model extending AbstractUser.
    Added attributes id, role.

    Attributes:
        id(UUID): Unique identifier for a user instance.
        role(CharField): Defines the role of the user.
    """

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('cafeadmin', 'CafeAdmin'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")

    def __str__(self) -> str:
        return f"{self.username}"
