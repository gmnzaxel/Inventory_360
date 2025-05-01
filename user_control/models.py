from django.db import models
from django.contrib.auth.models import AbstractUser
from control.models import Business

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')])
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.name} ({self.email})"

    def can_manage_business(self):
        return self.role == 'admin'

    def can_manage_products(self):
        return self.role == 'user'