import uuid
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.
class DiningTable(models.Model):
    """
    Model representing a dinningtable.

    Attributes:
        id (UUIDField): The unique identifier for the dinningtable
        table_number (PositiveIntegerField)- represents the table number
        created_at (DateTimeField): Timestamp when the dinningtable was created.
        updated_at (DateTimeField): Timestamp when the dinningtable was updated.
    """


    class Meta:
        verbose_name_plural = "Dining Tables"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_number = models.PositiveIntegerField(verbose_name="Table Number", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number}"
    
