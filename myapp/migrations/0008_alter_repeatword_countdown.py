# Generated by Django 4.1 on 2022-09-22 13:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_usersettings_hard_words_repeatword_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repeatword',
            name='countdown',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
