# Generated by Django 4.1 on 2022-09-25 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_repeatword_interval_alter_repeatword_countdown'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cefr_level',
            old_name='cefr_name',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(choices=[('Appearance', 'Проявление'), ('Communication', 'Коммуникация'), ('Culture', 'Культура'), ('Food and drink', 'Еда и напитки'), ('Functions', 'Функции'), ('Homes and buildings', 'Дома и строения'), ('Leisure', 'Свободное время'), ('Notions', 'Разное'), ('People', 'Люди'), ('Politics and society', 'Политика и народ'), ('Science and technology', 'Наука и технологии'), ('Sports', 'Спорт'), ('The natural world', 'Окружающий мир'), ('Time and space', 'Время и космос'), ('Travel', 'Путешествия'), ('Work and business', 'Работа и бизнес')], max_length=100),
        ),
    ]
