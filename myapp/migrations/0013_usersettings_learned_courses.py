# Generated by Django 4.1 on 2022-10-05 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_serverchoice_subcourse_videoobject_data_craftstack_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='learned_courses',
            field=models.ManyToManyField(blank=True, to='myapp.subcourse'),
        ),
    ]
