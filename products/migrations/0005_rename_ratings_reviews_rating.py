# Generated by Django 5.1.3 on 2024-11-19 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_reviews_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviews',
            old_name='ratings',
            new_name='rating',
        ),
    ]
