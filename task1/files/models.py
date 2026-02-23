from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone



class User(AbstractUser):
    class Meta:
        db_table='accounts'

def user_directory_path(instance, filename):
    return f"uploads/user_{instance.user.id}/{filename}"


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to=user_directory_path)
    original_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "userfiles"

    def __str__(self):
        return f"{self.original_name} - {self.user.email}"

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

