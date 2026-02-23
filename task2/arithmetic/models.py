from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser


class UserManager(BaseUserManager):
    """
    custom user manager to make email as the unique identifier instead of username
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided!")
        email=self.normalize_email(email)
        user=self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Super user must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Super user must have is_superuser=True')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Super user must have is_active=True')
        return self.create_user(email=email, password=password, **extra_fields)
class User(AbstractUser):
    username=None
    email=models.EmailField(unique=True)
    date_of_birth=models.DateField(null=True, blank=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name', 'date_of_birth']
    objects=UserManager()
    def __str__(self):
        return self.email
        

