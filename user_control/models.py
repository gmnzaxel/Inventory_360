from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from control.models import Business, Branch
from django.db.models import Q

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        username = extra_fields.pop('username', None) or email
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    PERMISSION_FLAGS = {
        'can_sale': 'ventas:execute',
        'can_purchase': 'compras:execute',
        'can_adjust': 'ajustes:execute',
        'can_transfer': 'transferencias:execute',
        'can_view_products': 'productos:read',
    }

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')])
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    can_purchase = models.BooleanField(default=False)
    can_sale = models.BooleanField(default=False)
    can_adjust = models.BooleanField(default=False)
    can_transfer = models.BooleanField(default=False)
    can_view_products = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(role='admin') | ~Q(branch__isnull=True),
                name='user_branch_required_for_non_admin'
            ),
        ]

    @property
    def permission_codes(self):
        codes = set()
        if self.role == 'admin':
            codes.add('admin:full')
        for field, code in self.PERMISSION_FLAGS.items():
            if getattr(self, field):
                codes.add(code)
        if self.role == 'admin':
            codes.add('productos:read')
        return sorted(codes)

    def has_permission(self, code: str) -> bool:
        return code in self.permission_codes

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = UserManager()
    def __str__(self):
        return f"{self.name} ({self.email})"





