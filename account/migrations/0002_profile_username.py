# Generated by Django 5.1.3 on 2024-11-22 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='username',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]
