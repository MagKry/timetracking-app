# Generated by Django 5.0.3 on 2024-03-26 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetracking_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.CharField(default='undefined', max_length=64),
            preserve_default=False,
        ),
    ]
