# Generated by Django 4.1 on 2022-10-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_usersettings_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersettings',
            name='email',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
