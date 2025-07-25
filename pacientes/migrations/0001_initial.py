# Generated by Django 5.2.2 on 2025-06-12 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('correo_electronico', models.EmailField(blank=True, max_length=254, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('fecha_nacimiento', models.DateField()),
                ('estatura', models.FloatField(help_text='Estatura en metros (ej: 1.75)')),
                ('ocupacion', models.CharField(max_length=100)),
                ('deportes', models.CharField(help_text='Deportes que practica', max_length=200)),
                ('horas_semana', models.CharField(help_text='Horas de ejercicio por semana', max_length=50)),
                ('alergias', models.TextField(blank=True, help_text='Alergias alimentarias o de otro tipo')),
                ('condiciones_especiales', models.TextField(blank=True, help_text='Condiciones médicas especiales')),
                ('objetivos', models.TextField(help_text='Objetivos nutricionales del paciente')),
                ('activo', models.BooleanField(default=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'db_table': 'pacientes',
            },
        ),
        migrations.CreateModel(
            name='PacienteNuevoB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('fecha_nacimiento', models.DateField()),
                ('estatura', models.FloatField()),
                ('peso', models.FloatField()),
                ('ocupacion', models.CharField(blank=True, max_length=100, null=True)),
                ('deportes', models.CharField(blank=True, max_length=100, null=True)),
                ('horas_semana', models.CharField(blank=True, max_length=100, null=True)),
                ('alergias', models.CharField(blank=True, max_length=100, null=True)),
                ('condiciones_especiales', models.TextField(blank=True, null=True)),
                ('objetivos', models.TextField(blank=True, null=True)),
                ('carbohidratos_g', models.FloatField(blank=True, null=True)),
                ('proteinas_g', models.FloatField(blank=True, null=True)),
                ('grasas_g', models.FloatField(blank=True, null=True)),
                ('calorias_totales', models.IntegerField(blank=True, null=True)),
                ('recomendaciones', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
