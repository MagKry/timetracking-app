# Generated by Django 5.0.3 on 2024-06-03 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracking_app', '0009_remove_loggedhours_employee_loggedhours_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]