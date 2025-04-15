from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')])

    def __str__(self):
        return self.name
