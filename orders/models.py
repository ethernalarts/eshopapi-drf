from django.db import models
from django.contrib.auth.models import User

from products.models import Product


# Create your models here.


class OrderStatus(models.TextChoices):
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class PaymentStatus(models.TextChoices):
    PAID = "PAID"
    NOT_PAID = "NOT_PAID"


class PaymentMode(models.TextChoices):
    COD = "COD (Cash on Delivery)"
    CARD = "CARD"


class Orders(models.Model):
    address = models.CharField(max_length=300, default="", blank=False)
    city = models.CharField(max_length=50, default="", blank=False)
    state = models.CharField(max_length=50, default="", blank=False)
    zipcode = models.IntegerField(default=0, blank=False)
    country = models.CharField(max_length=50, default="", blank=False)
    phone_number = models.CharField(max_length=20, default="", blank=False)
    email = models.EmailField(max_length=100, default="", blank=False)
    total_amount = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(
        max_length=50,
        choices = PaymentStatus.choices,
        default = PaymentStatus.NOT_PAID
    )
    order_status = models.CharField(
        max_length=50,
        choices = OrderStatus.choices,
        default = OrderStatus.PROCESSING
    )
    payment_mode = models.CharField(
        max_length=50,
        choices = PaymentMode.choices,
        default = PaymentMode.CARD
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class OrderItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, related_name='order_items')
    name = models.CharField(max_length=300, default="", blank=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)

    def __str__(self):
        return str(self.name)