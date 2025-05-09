from django.db import models
from django.contrib.auth.models import AbstractUser
from control.models import Business, Branch

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')])
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    # Nuevos permisos granulares
    can_purchase = models.BooleanField(default=False)
    can_sale = models.BooleanField(default=False)
    can_adjust = models.BooleanField(default=False)
    can_transfer = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.name} ({self.email})"