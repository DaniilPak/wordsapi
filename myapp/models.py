from pyexpat import model
from unicodedata import name
from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timezone

# Create your models here.

# Example model for examples in Oxford Word
class OxExample(models.Model):
    text = models.TextField(blank=True)
    translation_ru = models.TextField(blank=True)

    def __str__(self):
        return self.text

# Inflection model for inflections in Oxford Word
class Inflection(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class OxfordWord(models.Model):
    class CEFR_Level(models.TextChoices):
        A1_Beginner = 'A1', ('Beginner')
        A2_Elementary = 'A2', ('Elementary')
        B1_Intermediate = 'B1', ('Intermediate')
        B2_UpperIntermediate = 'B2', ('Upper-Intermediate')
        C1_Advanced = 'C1', ('Advanced')
        C2_Proficiency = 'C2', ('Proficiency')

    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=200, blank=True)
    translate_ru = models.CharField(max_length=200, blank=True)
    pronunciation_gb = models.FileField(upload_to='mp3s', blank=True)
    pronunciation_us = models.FileField(upload_to='mp3s', blank=True)
    spelling_gb = models.CharField(max_length=200)
    spelling_us = models.CharField(max_length=200)
    definition = models.TextField(blank=True)
    lexical_category = models.CharField(max_length=100)
    CEFR = models.CharField(max_length=2, choices=CEFR_Level.choices)
    topic = models.CharField(max_length=100, blank=True)
    examples = models.ManyToManyField(OxExample, blank=True)
    inflections = models.ManyToManyField(Inflection, blank=True)

    def __str__(self):
        return '%s %s %s %s %s' % (self.word, self.translate_ru, self.CEFR, self.id, self.topic)


# Holding User Data

class Topic(models.Model):

    name = models.CharField(max_length=100,
    # All themes are here, to add a new one, 
    # we start from here
    choices=[
            ('Appearance', 'Проявление'),
            ('Communication', 'Коммуникация'),
            ('Culture', 'Культура'),
            ('Food and drink', 'Еда и напитки'),
            ('Functions', 'Функции'),
            ('Homes and buildings', 'Дома и строения'),
            ('Leisure', 'Свободное время'),
            ('Notions', 'Разное'),
            ('People', 'Люди'),
            ('Politics and society', 'Политика и народ'),
            ('Science and technology', 'Наука и технологии'),
            ('Sports', 'Спорт'),
            ('The natural world', 'Окружающий мир'),
            ('Time and space', 'Время и космос'),
            ('Travel', 'Путешествия'),
            ('Work and business', 'Работа и бизнес'),
        ])

    def __str__(self):
        return '%s' % (self.name)

class CEFR_Level(models.Model):

    name = models.CharField(max_length=2,
    # All levels 
    choices=[
            ('A1', 'Beginner'),
            ('A2', 'Elementary'),
            ('B1', 'Intermediate'), 
            ('B2', 'Upper-Intermediate'),
            ('C1', 'Advanced'),
            ('C2', 'Proficiency')
        ])

    def __str__(self):
        return '%s' % (self.name)

# Repeat word
class RepeatWord(models.Model):
    oxford_word = models.ForeignKey(OxfordWord, blank=True, on_delete=models.CASCADE)
    countdown = models.DateTimeField(auto_now=True)
    interval = models.IntegerField(blank=True, default=0)

class UserSettings(models.Model):

    user_token = models.CharField(max_length=256)
    topics = models.ManyToManyField(Topic, blank=True)
    cefrs = models.ManyToManyField(CEFR_Level, blank=True)

    # Saved words
    # (Which are learned by user)
    learned_words = models.ManyToManyField(OxfordWord, blank=True)

    # Time to Repeat words
    repeat_words = models.ManyToManyField(RepeatWord, blank=True, related_name='repeatwords')

    # Hard words
    hard_words = models.ManyToManyField(OxfordWord, blank=True, related_name='hardwords')

### Courses ###

# Sections & Courses & SubCourses

class SubCourse(models.Model):
    id = models.AutoField(primary_key=True)
    subcourse_title = models.CharField(max_length=100)
    api_link = models.URLField()

class Data(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    img_uri = models.URLField()
    sub_courses = models.ManyToManyField(SubCourse)

class Course(models.Model):
    section = models.CharField(max_length=100)
    data = models.ManyToManyField(Data, blank=True)
    
# VideoObject that contains all data
# we need to create a full course

# Server choice is a part of VideoTest type component
# It give 4 choice buttons with 1 right answer

class ServerChoice(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField()

# Data from which we will craft 
# a course
class VideoObject(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.FileField(upload_to='grinavideos')
    tip = models.CharField(max_length=200)
    eng_text = models.CharField(max_length=200)
    ru_text = models.CharField(max_length=200)
    server_choice_1 = models.ForeignKey(ServerChoice, on_delete=models.CASCADE, related_name='sc1')
    server_choice_2 = models.ForeignKey(ServerChoice, on_delete=models.CASCADE, related_name='sc2')
    server_choice_3 = models.ForeignKey(ServerChoice, on_delete=models.CASCADE, related_name='sc3')
    server_choice_4 = models.ForeignKey(ServerChoice, on_delete=models.CASCADE, related_name='sc4')

    def __str__(self) -> str:
        return '%s' % (self.id)

# Stack Of VideoObject
# we will get JSON data from this object
class CraftStack(models.Model):
    
    id = models.AutoField(primary_key=True)
    video_objects = models.ManyToManyField(VideoObject, blank=True)

    def __str__(self) -> str:
        return '%s' % (self.id)