from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver


# Create your models here.


class Category(models.TextChoices):
    ELECTRONICS = "Electronics"
    LAPTOPS = "Laptops"
    ARTS = "Arts"
    FOOD = "Food"
    HOME = "Home"
    KITCHEN = "Kitchen"


class Product(models.Model):
    name = models.CharField(max_length=200, default="", blank=False)
    description = models.TextField(max_length=1000, default="", blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    brand = models.CharField(max_length=200, default="", blank=False)
    category = models.CharField(max_length=30, choices=Category.choices)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products_product'

    def __str__(self):
        return self.name


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="images")
    image = models.ImageField(upload_to="products")


# Signals
@receiver(post_delete, sender=ProductImages)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    username = models.EmailField(blank=True, max_length=254)
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return str(self.comment)