# Generated by Django 4.1 on 2022-09-22 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_repeatword_countdown'),
    ]

    operations = [
        migrations.AddField(
            model_name='repeatword',
            name='interval',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='repeatword',
            name='countdown',
            field=models.DateTimeField(auto_now=True),
        ),
    ]