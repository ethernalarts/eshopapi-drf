# Generated by Django 5.1.3 on 2024-11-22 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_profile_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='username',
        ),
    ]
