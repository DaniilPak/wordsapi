from pyexpat import model
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
            ('Appearance', 'Appearance'),
            ('Communication', 'Communication'),
            ('Culture', 'Culture'),
            ('Food and drink', 'Food and drink'),
            ('Functions', 'Functions'),
            ('Homes and buildings', 'Homes and buildings'),
            ('Leisure', 'Leisure'),
            ('Notions', 'Notions'),
            ('People', 'People'),
            ('Politics and society', 'Politics and society'),
            ('Science and technology', 'Science and technology'),
            ('Sports', 'Sports'),
            ('The natural world', 'The natural world'),
            ('Time and space', 'Time and space'),
            ('Travel', 'Travel'),
            ('Work and business', 'Work and business'),
        ])

    def __str__(self):
        return '%s' % (self.name)

class CEFR_Level(models.Model):

    cefr_name = models.CharField(max_length=2,
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
        return '%s' % (self.cefr_name)

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


