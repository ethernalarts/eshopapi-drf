# Generated by Django 5.1.3 on 2024-11-23 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_status',
            field=models.CharField(choices=[('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('CANCELED', 'Canceled')], default='PROCESSING', max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='payment_status',
            field=models.CharField(choices=[('PAID', 'Paid'), ('NOT_PAID', 'Not Paid')], default='NOT_PAID', max_length=50),
        ),
    ]
