# Generated by Django 4.1 on 2022-10-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_usersettings_learned_courses'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='email',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]
