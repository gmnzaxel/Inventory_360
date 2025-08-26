from django.db import models
from django.conf import settings

class Business(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(default="")
    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='branches')
    def __str__(self):
        return f"{self.name} - {self.business.name}"

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    def __str__(self):
        return f"{self.name} ({self.business.name})"

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('purchase_order', 'Purchase Order'),
        ('adjustment_note', 'Adjustment Note'),
        ('transfer_note', 'Transfer Note'),
    ]
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.document_type} #{self.document_number}"

class Supplier(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
    ]
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='movements_to')
    branch_from = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity}) from {self.branch_from} to {self.branch}"

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    class Meta:
        unique_together = ('product', 'branch')
    def __str__(self):
        return f"{self.product.name} in {self.branch.name}: {self.quantity}"