# Generated by Django 5.0.6 on 2024-06-30 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicio', '0012_programacion_fecha_impreso_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='casinocolacion',
            name='_syncing',
            field=models.BooleanField(default=False),
        ),
    ]
