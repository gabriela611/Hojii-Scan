# Generated by Django 5.1.7 on 2025-04-01 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extraction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extractedresume',
            name='profession',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
