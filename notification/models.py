from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()
class Notification(models.Model):
    """
    Model representing notifications sent to users.
    
    Attributes:
        user (ForeignKey): The user the notification is sent to.
        message (CharField): The notification message.
        is_read (BooleanField): Tracks whether the notification has been read.
        created_at (DateTimeField): When the notification was created.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Notifications"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

