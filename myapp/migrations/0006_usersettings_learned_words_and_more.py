# Generated by Django 4.1 on 2022-09-22 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_cefr_level_topic_usersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='learned_words',
            field=models.ManyToManyField(blank=True, to='myapp.oxfordword'),
        ),
        migrations.AlterField(
            model_name='cefr_level',
            name='cefr_name',
            field=models.CharField(choices=[('A1', 'Beginner'), ('A2', 'Elementary'), ('B1', 'Intermediate'), ('B2', 'Upper-Intermediate'), ('C1', 'Advanced'), ('C2', 'Proficiency')], max_length=2),
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(choices=[('Appearance', 'Appearance'), ('Communication', 'Communication'), ('Culture', 'Culture'), ('Food and drink', 'Food and drink'), ('Functions', 'Functions'), ('Homes and buildings', 'Homes and buildings'), ('Leisure', 'Leisure'), ('Notions', 'Notions'), ('People', 'People'), ('Politics and society', 'Politics and society'), ('Science and technology', 'Science and technology'), ('Sports', 'Sports'), ('The natural world', 'The natural world'), ('Time and space', 'Time and space'), ('Travel', 'Travel'), ('Work and business', 'Work and business')], max_length=100),
        ),
    ]