from django.db import models, transaction
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.functions import Lower

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'business',
                name='uniq_branch_business_name_ci'
            ),
        ]
        indexes = [
            models.Index(Lower('name'), name='idx_branch_lower_name'),
        ]

    def __str__(self):
        return f"{self.name} - {self.business.name}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'business',
                name='uniq_category_business_name_ci'
            ),
        ]
        indexes = [
            models.Index(Lower('name'), name='idx_category_lower_name'),
        ]

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    image = models.URLField(max_length=200, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'business',
                name='uniq_product_business_name_ci'
            ),
        ]
        indexes = [
            models.Index(Lower('name'), name='idx_product_lower_name'),
        ]

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
    document_number = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.document_type} #{self.document_number}"
    class Meta:
        unique_together = (('business', 'document_type', 'document_number'),)

class Movement(models.Model):
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
    ]
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='movements_to')
    branch_from = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements_from')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity}) from {self.branch_from} to {self.branch}"

@receiver(post_save, sender=Movement)
def update_stock_on_movement(sender, instance, created, **kwargs):
    """Apply stock effects on movement creation.

    Note: Updates and deletions are handled in dedicated signals to ensure
    consistent stock adjustments across lifecycle changes.
    """
    if created:
        with transaction.atomic():
            stock_to, _ = Stock.objects.get_or_create(
                product=instance.product,
                branch=instance.branch,
                defaults={'quantity': 0, 'minimum_stock': 10}
            )
            stock_to.quantity += instance.quantity
            stock_to.save()

            if instance.movement_type == 'transfer' and instance.branch_from:
                stock_from, _ = Stock.objects.get_or_create(
                    product=instance.product,
                    branch=instance.branch_from,
                    defaults={'quantity': 0, 'minimum_stock': 10}
                )
                stock_from.quantity -= instance.quantity
                stock_from.save()

from django.db.models.signals import pre_save, pre_delete


@receiver(pre_save, sender=Movement)
def reconcile_stock_on_movement_update(sender, instance, **kwargs):
    """Revert old movement impact and apply new impact when updating.

    This runs before saving an existing Movement (instance.pk is set).
    """
    if not instance.pk:
        return  # Only handle updates

    try:
        old = Movement.objects.get(pk=instance.pk)
    except Movement.DoesNotExist:
        return

    # If nothing relevant changed, skip
    relevant_changed = (
        old.product_id != instance.product_id or
        old.branch_id != instance.branch_id or
        old.branch_from_id != instance.branch_from_id or
        old.quantity != instance.quantity
    )
    if not relevant_changed:
        
        return

    with transaction.atomic():
        # Revert old impact
        stock_to_old, _ = Stock.objects.get_or_create(
            product=old.product,
            branch=old.branch,
            defaults={'quantity': 0, 'minimum_stock': 10}
        )
        stock_to_old.quantity -= old.quantity
        stock_to_old.save()

        if old.movement_type == 'transfer' and old.branch_from_id:
            stock_from_old, _ = Stock.objects.get_or_create(
                product=old.product,
                branch=old.branch_from,
                defaults={'quantity': 0, 'minimum_stock': 10}
            )
            stock_from_old.quantity += old.quantity
            stock_from_old.save()

        # Apply new impact
        stock_to_new, _ = Stock.objects.get_or_create(
            product=instance.product,
            branch=instance.branch,
            defaults={'quantity': 0, 'minimum_stock': 10}
        )
        stock_to_new.quantity += instance.quantity
        stock_to_new.save()

        if instance.movement_type == 'transfer' and instance.branch_from_id:
            stock_from_new, _ = Stock.objects.get_or_create(
                product=instance.product,
                branch=instance.branch_from,
                defaults={'quantity': 0, 'minimum_stock': 10}
            )
            stock_from_new.quantity -= instance.quantity
            stock_from_new.save()


@receiver(pre_delete, sender=Movement)
def revert_stock_on_movement_delete(sender, instance, **kwargs):
    """Revert stock effects when a movement is deleted."""
    with transaction.atomic():
        # Revert effect on destination branch
        stock_to, _ = Stock.objects.get_or_create(
            product=instance.product,
            branch=instance.branch,
            defaults={'quantity': 0, 'minimum_stock': 10}
        )
        stock_to.quantity -= instance.quantity
        stock_to.save()

        # For transfers, also revert origin branch
        if instance.movement_type == 'transfer' and instance.branch_from_id:
            stock_from, _ = Stock.objects.get_or_create(
                product=instance.product,
                branch=instance.branch_from,
                defaults={'quantity': 0, 'minimum_stock': 10}
            )
            stock_from.quantity += instance.quantity
            stock_from.save()

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    class Meta:
        unique_together = ('product', 'branch')
    def __str__(self):
        return f"{self.product.name} in {self.branch.name}: {self.quantity}"
