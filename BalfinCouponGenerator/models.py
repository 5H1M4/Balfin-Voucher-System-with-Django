from django.db import models
from django.utils import timezone
from datetime import timedelta

class Coupon(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    barcode = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)  # New field to track active status
    is_used = models.BooleanField(default=False) #delete this line along with table head and table data in the html call
   #created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the creation timestamp

    def save(self, *args, **kwargs):
        # Automatically generate expiration date if not provided
        if not self.expiration_date:
            self.expiration_date = timezone.now().date() + timedelta(days=60)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Coupon {self.barcode} - Amount: {self.amount} - Expires on: {self.expiration_date}"

    STATUS_CHOICES = [
        ('not active', 'Not Active'),
        ('active', 'Active'),
        ('used', 'Used'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='not active')
