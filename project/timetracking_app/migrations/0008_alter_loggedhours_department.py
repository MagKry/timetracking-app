# Generated by Django 5.0.3 on 2024-04-04 21:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracking_app', '0007_loggedhours_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loggedhours',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='timetracking_app.department'),
        ),
    ]
