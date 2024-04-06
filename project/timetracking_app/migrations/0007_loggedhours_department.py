# Generated by Django 5.0.3 on 2024-04-04 20:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracking_app', '0006_remove_loggedhours_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='loggedhours',
            name='department',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='timetracking_app.department'),
            preserve_default=False,
        ),
    ]