# Generated by Django 5.1.7 on 2025-03-24 03:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedResume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('job_title', models.CharField(blank=True, max_length=255, null=True)),
                ('contact', models.TextField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('professional_experience', models.TextField(blank=True, null=True)),
                ('education', models.JSONField(blank=True, default=list, null=True)),
                ('achievements', models.TextField(blank=True, null=True)),
                ('expertise', models.TextField(blank=True, null=True)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
        ),
    ]
