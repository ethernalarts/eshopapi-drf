# Generated by Django 5.1.3 on 2024-11-29 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_rename_zip_code_orders_zipcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='image',
            field=models.CharField(default='', max_length=500),
        ),
    ]
