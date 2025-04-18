# Generated by Django 5.1.7 on 2025-03-22 19:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv_forms', '0004_personalinfo_fecha_nacimiento_personalinfo_genero'),
    ]

    operations = [
        migrations.CreateModel(
            name='HabilidadesCompetencias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilidades_tecnicas', models.TextField(blank=True, help_text='Ejemplo: Python, SQL, Redes', null=True)),
                ('cualidades_personales', models.TextField(blank=True, help_text='Ejemplo: Responsable, puntual, trabajo en equipo', null=True)),
                ('idiomas', models.TextField(blank=True, help_text='Ejemplo: Español nativo, Inglés B1', null=True)),
                ('trabajo_deseado', models.CharField(blank=True, help_text='Ejemplo: Busco empleo como desarrollador backend en tecnología Python', max_length=255, null=True)),
                ('personal_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='habilidades', to='cv_forms.personalinfo')),
            ],
        ),
    ]
