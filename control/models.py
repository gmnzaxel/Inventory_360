from django.db import models

class Business(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(default="")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('output', 'Output')
    ]
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    document_number = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.movement_type} - {self.product_name} ({self.quantity})"
