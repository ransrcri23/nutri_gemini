# Generated by Django 5.2.2 on 2025-06-16 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valoraciones', '0002_valoracion_tabla_equivalencias'),
    ]

    operations = [
        migrations.AddField(
            model_name='valoracion',
            name='plan_comidas',
            field=models.TextField(blank=True, help_text='Plan de comidas diarias con horarios y macronutrientes', null=True),
        ),
    ]
