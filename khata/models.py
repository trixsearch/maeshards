from django.db import models
from django.utils import timezone
import random

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} available)"

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(default=timezone.now)
    customer_name = models.CharField(max_length=100, blank=True) 
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_address = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number

    @classmethod
    def generate_invoice_number(cls):
        date_str = timezone.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        return f"INV-{date_str}-{random_str}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

class InventoryLoss(models.Model):
    LOSS_REASONS = [
        ('DAMAGED', 'Damaged Goods'),
        ('EXPIRED', 'Expired Products'),
        ('THEFT', 'Theft'),
        ('OTHER', 'Other Reasons'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=LOSS_REASONS)
    loss_value = models.DecimalField(max_digits=10, decimal_places=2)
    loss_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate loss value
        self.loss_value = self.product.cost_price * self.quantity
        super().save(*args, **kwargs)