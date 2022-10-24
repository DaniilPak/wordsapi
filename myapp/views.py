from http import server
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import *

# Import to process
# django data to JSON
# import requests
import json

# Import to get random amount of words
import random

# To fix JSON objects and adapt from 
# django objects to correct JSON objects
from django.core import serializers

# Imported for filtering 
# Onjects that are already
# learned
from django.db.models import Q, F

# Hash 256
from hashlib import sha256

# Import to convert str array taken from 
# Frontend to python array
from ast import literal_eval

# To Allow POST without csrf token
from django.views.decorators.csrf import csrf_exempt

# Date to substructing
from datetime import datetime, timezone, timedelta

# Create your views here.

# Register, Login, Saving Progress

@csrf_exempt
def register_new_user(request):
    
    # Getting POSTed data
    email = request.POST['email']
    password = request.POST['password']

    # Getting POSTed topics and levels
    posted_topics = request.POST['topics']
    posted_levels = request.POST['levels']

    # concat email & pass to create a sha256
    input_ = email + password

    # Generate token 8 length token
    user_token = sha256(input_.encode('utf-8')).hexdigest()[:8]

    # Create UserSettings and set user token
    user_settings = UserSettings(user_token=user_token, email=email)
    # Record user's email
    user_settings.save()

    # Digest given array in str format
    # Levels and Topics given:
    # This format ['A1', 'B1', 'C2']
    lvls_str = posted_levels
    # Converting string to python array
    lvls_to_array = literal_eval(lvls_str)
    # Iterating over this array to get the real objects
    for lvl in lvls_to_array:
        current_cefr_obj = CEFR_Level.objects.get(name=lvl)
        # Finally adding Cefr to user settings object
        user_settings.cefrs.add(current_cefr_obj)

    # Now the topics time
    # This format ['RUS', 'GER', 'FRA']
    topics_str = posted_topics
    topics_to_array = literal_eval(topics_str)

    for topic in topics_to_array:
        current_topic_obj = Topic.objects.get(name=topic)
        user_settings.topics.add(current_topic_obj)


    # Giving user_token to user
    user_token_list = {
        'user_token': user_token
    }

    return JsonResponse(user_token_list, safe=False)

def index(request, token):
    # Get user's settings by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Get array of topics from userSettings
    topics = []
    cefrs = []

    # Iterate over topics
    for topic in user_settings.topics.all():
        topics.append(topic)
    
    # Iterate over cefrs
    for level in user_settings.cefrs.all():
        cefrs.append(level)

    # Handle passed words and filter them by levels and topics
    passed_words = user_settings.passed_words.all().filter(CEFR__in=cefrs, topic__in=topics)

    # Iterate over passed words to create array with only ids
    ids = []
    for lw in passed_words:
        ids.append(lw.id)

    # This filteres words that are already on learning
    # ~ has a mirroring effect
    filtered_oxs = OxfordWord.objects.filter(~Q(id__in=ids))

    # 
    items = list(filtered_oxs.filter(CEFR__in=cefrs, topic__in=topics))

    # change 3 to how many random items you want
    # Deprecated code, don't need to take random ones
    # instead taking first [amount of words] used
    # words_taken_from_api = random.sample(items, 5)
    # or items[:10] just column

    # What if item lenght is less that 10?
    # Do this logic:
    objects_amount = len(items) if len(items) < 10 else 10


    # change num to take exact amount
    words_taken_from_api = random.sample(items, objects_amount)

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', words_taken_from_api)

    # Edit Native JSON to format, that App need

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])

    return JsonResponse(fixed_oxford_words, safe=False)

# This view gets learned words 
# and sets to UserSettings accountant

# Get More words to Flat List
@csrf_exempt
def get_more_words(request):

    # GET token 
    token = request.POST['token']

    # Get array of learned words
    learned_ids = request.POST['learned']
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Format array with words
    learned_ids_to_array = literal_eval(learned_ids)

    # Get array of topics from userSettings
    topics = []
    cefrs = []

    # Iterate over topics
    for topic in user_settings.topics.all():
        topics.append(topic)
    
    # Iterate over cefrs
    for level in user_settings.cefrs.all():
        cefrs.append(level)

    # Id not in learned ids to array
    filtered_oxs = OxfordWord.objects.filter(~Q(id__in=learned_ids_to_array))
    
    items = list(filtered_oxs.filter(CEFR__in=cefrs, topic__in=topics))

    # change 3 to how many random items you want
    # Deprecated code, don't need to take random ones
    # instead taking first [amount of words] used
    # words_taken_from_api = random.sample(items, 5)
    # or items[:10] just column

    # What if item lenght is less that 10?
    # Do this logic:
    objects_amount = len(items) if len(items) < 10 else 10

    # change num to take exact amount
    words_taken_from_api = random.sample(items, objects_amount)

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', words_taken_from_api)

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])


    return JsonResponse(fixed_oxford_words, safe=False)

@csrf_exempt
def save_learned_words(request):
    # GET token 
    token = request.POST['token']

    # Get array of learned words
    learned_ids = request.POST['learned']
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    if(learned_ids):
        # Format array with words
        learned_ids_to_array = literal_eval(learned_ids)

        # Iterating over this array to get the real objects
        for learned_word_id in learned_ids_to_array:
            oxford_word = OxfordWord.objects.get(id=learned_word_id)
            # 
            user_settings.learned_words.add(oxford_word)
            # Add Repeat Words
            # Time is automatically added
            r_word = RepeatWord.objects.create(oxford_word=oxford_word)
            user_settings.repeat_words.add(r_word)
        
    return HttpResponse("Query complete.")

# Save passed words
### Dont ever forget csrf_exempt
@csrf_exempt
def save_passed_words(request):
    # GET token 
    token = request.POST['token']

    # Get array of repeated words
    hard_ids = request.POST['passed']

    # Format array with words
    hard_ids_to_array = literal_eval(hard_ids)

    # Transform word ids to real objects
    hard_words_objects = OxfordWord.objects.filter(Q(id__in=hard_ids_to_array))
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Save detected hard words to user settings model
    for hwo in hard_words_objects:
        user_settings.passed_words.add(hwo)
        user_settings.save()
    
    # End of story

    return HttpResponse("Query complete.")

# API All my words
def my_word(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', user_settings.learned_words.all())

    # Edit Native JSON to format, that App need

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])

    return JsonResponse(fixed_oxford_words, safe=False)

# API Repeat word

def repeat_words(request):

    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Check current time
    now = datetime.now(timezone.utc)

    # Get Repeat Word objects from user data
    repeat_words = user_settings.repeat_words.all()

    # Future JSON object
    timeleft_words = list()

    # Check how much time left (in seconds)
    for r_word in repeat_words:
        # Interval formula Y = 2X + 1
        y_days = (2 * r_word.interval) + 1
        if now - r_word.countdown > timedelta(days=y_days):
            timeleft_words.append(r_word.oxford_word)

    # Format to right JSON

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', timeleft_words)

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])

    return JsonResponse(fixed_oxford_words, safe=False)

# Hard words 

def hard_word(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', user_settings.hard_words.all())

    # Edit Native JSON to format, that App need

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])

    return JsonResponse(fixed_oxford_words, safe=False)

# User Settings changing after registration

# Change levels after registration
def change_level(request):
    # GET token
    token = request.POST['token']

    # Get new levels array (str format)
    new_levels = request.POST['levels']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Digest given array in str format
    # Levels and Topics given:
    # This format ['A1', 'B1', 'C2']
    lvls_str = new_levels

    # Converting string to python array
    lvls_to_array = literal_eval(lvls_str)

    # Clear levels in UserSettings
    user_settings.cefrs.clear()

    # Iterating over this array to get the real objects
    for lvl in lvls_to_array:
        current_cefr_obj = CEFR_Level.objects.get(name=lvl)
        # Finally adding Cefr to user settings object
        user_settings.cefrs.add(current_cefr_obj)

    # Formality
    return HttpResponse("Query complete.")

# Change topics after registration
def change_topic(request):
    # GET token
    token = request.POST['token']

    # Get new levels array (str format)
    new_topics = request.POST['topics']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Digest given array in str format
    # Levels and Topics given:
    # This format ['A1', 'B1', 'C2']
    topics_str = new_topics

    # Converting string to python array
    topics_to_array = literal_eval(topics_str)

    # Clear levels in UserSettings
    user_settings.topics.clear()

    # Iterating over this array to get the real objects
    for topic in topics_to_array:
        current_topic = Topic.objects.get(name=topic)
        # Finally adding Cefr to user settings object
        user_settings.topics.add(current_topic)

    # Formality
    return HttpResponse("Query complete.")

# Get users topics
def get_users_topic(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)
    user_topics = user_settings.topics.all()

    all_topics = Topic.objects.all()

    # Future JSON object
    fixed_topics = list()

    # Processing each object
    for idx, item in enumerate(serializers.serialize('python', all_topics)):
        # Check if my topic checked in all topics
        checked = False
        for ut in user_topics:
            if ut.name == item['fields']['name']:
                checked = True

        topic = Topic.objects.get(name=item['fields']['name'])
        item['fields']['repr'] = topic.get_name_display()
        item['fields']['checked'] = checked
        fixed_topics.append(item['fields'])

    # JSON object will have checked boolean true, if 
    # Topic already choosed by user

    return JsonResponse(fixed_topics, safe=False)

# Get users topics
def get_users_level(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)
    user_cefrs = user_settings.cefrs.all()

    all_cefrs = CEFR_Level.objects.all()

    # Future JSON object
    fixed_levels = list()

    # Processing each object
    for idx, item in enumerate(serializers.serialize('python', all_cefrs)):
        # Check if my topic checked in all topics
        checked = False
        for ul in user_cefrs:
            if ul.name == item['fields']['name']:
                checked = True

        topic = CEFR_Level.objects.get(name=item['fields']['name'])
        item['fields']['repr'] = topic.get_name_display()
        item['fields']['checked'] = checked
        fixed_levels.append(item['fields'])

    # JSON object will have checked boolean true, if 
    # Topic already choosed by user

    return JsonResponse(fixed_levels, safe=False)

# Get users words amount 
def get_users_my_words_amount(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    mywords_count = user_settings.learned_words.count()

    arr_for_deploy = {
        'count': mywords_count
    }

    return JsonResponse(arr_for_deploy, safe=False)

# Get users repeat words amount 
def get_users_repeat_words_amount(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Check current time
    now = datetime.now(timezone.utc)

    repeat_words = user_settings.repeat_words.all()

    # Future JSON object
    timeleft_words = 0

    # Check how much time left (in seconds)
    for r_word in repeat_words:
        # Interval formula Y = 2X + 1
        y_days = (2 * r_word.interval) + 1
        if now - r_word.countdown > timedelta(days=y_days):
            timeleft_words += 1

    arr_for_deploy = {
        'count': timeleft_words
    }

    return JsonResponse(arr_for_deploy, safe=False)

# Get users repeat words amount 
def get_users_hard_words_amount(request):
    # GET token
    token = request.GET['token']

    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    mywords_count = user_settings.hard_words.count()

    arr_for_deploy = {
        'count': mywords_count
    }

    return JsonResponse(arr_for_deploy, safe=False)


### Get repeated words, and increase their interval ###
@csrf_exempt
def renew_repeated_words(request):
    # GET token 
    token = request.POST['token']

    # Get array of repeated words
    repeated_ids = request.POST['repeated']

    # Format array with words
    repeated_ids_to_array = literal_eval(repeated_ids)

    # Transform word ids to real objects
    repeated_words_objects = OxfordWord.objects.filter(Q(id__in=repeated_ids_to_array))
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Get repeat words using filter by ids
    user_settings.repeat_words.all().filter(Q(oxford_word__in=repeated_words_objects)).update(interval=F('interval') + 1)

    # End of story

    return HttpResponse("Query complete.")

### Also detect hard ones and store them
@csrf_exempt
def detect_hard_words(request):
    # GET token 
    token = request.POST['token']

    # Get array of repeated words
    hard_ids = request.POST['hard']

    # Format array with words
    hard_ids_to_array = literal_eval(hard_ids)

    # Transform word ids to real objects
    hard_words_objects = OxfordWord.objects.filter(Q(id__in=hard_ids_to_array))
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    # Save detected hard words to user settings model
    for hwo in hard_words_objects:
        user_settings.hard_words.add(hwo)
        user_settings.save()
    
    # End of story

    return HttpResponse("Query complete.")

### Lets add removing hard words (after successfull repeating)
### Also detect hard ones and store them
@csrf_exempt
def delete_hard_words(request):
    # GET token 
    token = request.POST['token']

    # Get array of repeated words
    abort_hard = request.POST['aborthard']

    # Format array with words
    abort_hard_to_array = literal_eval(abort_hard)

    # Transform word ids to real objects
    hard_words_objects = OxfordWord.objects.filter(Q(id__in=abort_hard_to_array))
    
    # Handle current UserSettings object by token
    user_settings = UserSettings.objects.get(user_token=token)

    for hwo in hard_words_objects:
        user_settings.hard_words.remove(hwo)
    
    # End of story

    return HttpResponse("Query complete.")


### MISC ###

# Get all level (for registration)
def get_all_level(request):

    all_cefrs = CEFR_Level.objects.all()

    # Future JSON object
    fixed_levels = list()

    # Processing each object
    for idx, item in enumerate(serializers.serialize('python', all_cefrs)):
        topic = CEFR_Level.objects.get(name=item['fields']['name'])
        item['fields']['repr'] = topic.get_name_display()
        fixed_levels.append(item['fields'])

    # JSON object will have checked boolean true, if 
    # Topic already choosed by user

    return JsonResponse(fixed_levels, safe=False)

# Get users topics
def get_all_topic(request):

    all_topics = Topic.objects.all()

    # Future JSON object
    fixed_topics = list()

    # Processing each object
    for idx, item in enumerate(serializers.serialize('python', all_topics)):
        topic = Topic.objects.get(name=item['fields']['name'])
        item['fields']['repr'] = topic.get_name_display()
        fixed_topics.append(item['fields'])

    # JSON object will have checked boolean true, if 
    # Topic already choosed by user

    return JsonResponse(fixed_topics, safe=False)


# Get dummy words
def get_dummy(request):

    count = request.GET['count']

    owords = OxfordWord.objects.all()

    random_owords = random.sample(list(owords), int(count))

    # Convert to JSON
    django_to_json_object = serializers.serialize('python', random_owords)

    # Edit Native JSON to format, that App need

    # Future JSON object
    fixed_oxford_words = list()

    # Processing each object
    for idx, item in enumerate(django_to_json_object):
        # Get current item OxfordWord object duplicate to
        # get examples and inflections in serialized python 
        # format
        current_items_oxfordword_object = OxfordWord.objects.get(id=item['pk'])

        # Convert django object to JSON
        current_items_inflections = serializers.serialize('python', current_items_oxfordword_object.inflections.all())
        current_items_examples = serializers.serialize('python', current_items_oxfordword_object.examples.all())

        # Fix gotten JSON object
        arr_for_fixed_inflections = list()
        arr_for_fixed_examples = list()

        # Fixing inflections
        for inflection_item in current_items_inflections:
            arr_for_fixed_inflections.append(inflection_item['fields'])

        # Equaling gotten inflections to item
        item['fields']['inflections'] = arr_for_fixed_inflections

         # Fixing examples
        for example_item in current_items_examples:
            arr_for_fixed_examples.append(example_item['fields'])

        # Equaling gotten examples to item
        item['fields']['examples'] = arr_for_fixed_examples
        
        # Setting id to word object
        item['fields']['id'] = item['pk']

        fixed_oxford_words.append(item['fields'])

    return JsonResponse(fixed_oxford_words, safe=False)

'''
Registration stuff:
- Check if email already exists
- Auth into existing account 
'''
def check_if_email_exists(request, email):

    '''
    Getting requested email to check from url
    '''
    isExists = True

    try:
        user_settings = UserSettings.objects.get(email=email)
    except UserSettings.DoesNotExist:
        isExists = False

    arr_for_deploy = {
        'email_exists': isExists
    }

    return JsonResponse(arr_for_deploy, safe=False)

def auth_into_existing_account(request):

    email = request.POST['email']
    password = request.POST['password']

    # concat email & pass to create a sha256
    input_ = email + password

    # Generate token 8 length token
    given_sha256 = sha256(input_.encode('utf-8')).hexdigest()[:8]

    # Check if that token exists in system
    isCredentialsCorrect = True
    user_token = ''

    try:
        user_settings = UserSettings.objects.get(user_token=given_sha256)
        user_token = user_settings.user_token
    except UserSettings.DoesNotExist:
        isCredentialsCorrect = False
        user_token = 'notexist'

    arr_for_deploy = {
        'email_exists': isCredentialsCorrect,
        'user_token': user_token
    }

    return JsonResponse(arr_for_deploy, safe=False)

def auth_via_google(request):
    '''
    Get user's google email and check if it's already exists
    if yes: get users existing token and send it
    if not: create new token and send it
    '''
    google_mail = request.POST['googlemail']
    google_name = request.POST['googlename']

    posted_topics = request.POST['topics']
    posted_levels = request.POST['levels']

    user_exists = True
    user_token = ''
    try:
        user_settings = UserSettings.objects.get(email=google_mail)
        user_token = user_settings.user_token
    except UserSettings.DoesNotExist:
        user_exists = False
        # Code if user with given email does not exists
        input_ = google_mail + google_name
        # Generate token 8 length token
        user_token = sha256(input_.encode('utf-8')).hexdigest()[:8]
        user_settings = UserSettings(user_token=user_token, email=google_mail)

        lvls_str = posted_levels
        lvls_to_array = literal_eval(lvls_str)
        for lvl in lvls_to_array:
            current_cefr_obj = CEFR_Level.objects.get(name=lvl)
            user_settings.cefrs.add(current_cefr_obj)

        topics_str = posted_topics
        topics_to_array = literal_eval(topics_str)

        for topic in topics_to_array:
            current_topic_obj = Topic.objects.get(name=topic)
            user_settings.topics.add(current_topic_obj)

        user_settings.save()

    arr_for_deploy = {
        'user_exists': user_exists, 
        'user_token': user_token
    }

    return JsonResponse(arr_for_deploy, safe=False)

### COURSES ###

# API for courses & videotests(videocards)

def index_courses(request, token):

    # Hook current UserSettings model to identify user
    user_settings = UserSettings.objects.get(user_token=token)

    course_objects = serializers.serialize('json', Course.objects.all())
    course_objects_to_json = json.loads(course_objects)
    # New future json object
    courses_fixed_json = list()

    # Fixing Course objects
    for idx, item in enumerate(course_objects_to_json):
        # New stuff
        current_course = Course.objects.get(id=idx+1)
        course_datas = serializers.serialize('python', current_course.data.all())
        item['fields']['section'] = current_course.section
        item['fields']['data'] = course_datas

        # Fixing Data objects
        for idx2, data_item in enumerate(course_datas):
            # Hooking current Data object from Data object primary key  
            current_data = Data.objects.get(pk=json.loads(json.dumps(data_item))['pk'])
            # Removing superfluos from data object in json
            x = serializers.serialize('python', [current_data])
            item['fields']['data'][idx2] = x[0]['fields']
            # Adding id field to data json object
            item['fields']['data'][idx2]['id'] = x[0]['pk']
            # Hooking current SubCourses object from current Data object
            current_datas_subcourses =  serializers.serialize('python', current_data.sub_courses.all())
            item['fields']['data'][idx2]['sub_courses'] = current_datas_subcourses

            # Fixing SubCourse objects
            for idx3, subcourse_item in enumerate(current_datas_subcourses):
                current_subcourse = SubCourse.objects.get(pk=json.loads(json.dumps(subcourse_item))['pk'])
                y = serializers.serialize('python', [current_subcourse])
                item['fields']['data'][idx2]['sub_courses'][idx3] = y[0]['fields']
                # Checking if subcourse been learned by User
                # Put some logic here ...
                users_learned_subcourses = user_settings.learned_courses.all()
                # Find if user have current subcourse
                learned = False
                if current_subcourse in users_learned_subcourses:
                    learned = True

                item['fields']['data'][idx2]['sub_courses'][idx3]['learned'] = learned
                # Add pk of subcourse
                item['fields']['data'][idx2]['sub_courses'][idx3]['id'] = current_subcourse.pk

        # Saving all processed data to future json object
        courses_fixed_json.append(item['fields'])
 
    return JsonResponse(courses_fixed_json, safe=False)

# Get Video Object and craft a 
# course with given object's data

def get_craft(request, craft_id):

    # Get current Video Object
    video_objects = CraftStack.objects.get(id=craft_id).video_objects.all()

    # Init a void array to hold future data
    valid_json_video_objects = list()

    # Iterate over video_object items
    # and create cards
    for item in video_objects:
        item_to_json = serializers.serialize('python', [item])
        # Append to void array only 'field' JSON object
        valid_json_video_objects.append(item_to_json[0]['fields'])

    # At this point we have a list with all 
    # Video Objects in current course
    # Lets create a new one list to 
    # craft and append cards, videotests, parts etc...

    # craft array is a final result to show up
    craft = list()

    # Iterate over Video Objects we have
    for video_obj in valid_json_video_objects:
        # Craft cards
        card_json_object = {
            'type': 'card',
            'source': video_obj['source'],
            'eng_text': video_obj['eng_text'],
            'ru_text': video_obj['ru_text'],
            'tip': video_obj['tip'],
        }
        # append result of crafted cards
        craft.append(card_json_object)

    # Iterate over Video Objects again for tests
    choices = list()

    for video_obj in valid_json_video_objects:
        for sc in video_obj['server_choices']:
            server_choice = ServerChoice.objects.get(pk=sc)
            ss = serializers.serialize('python', [server_choice])
            choices.append(ss[0]['fields'])

        # Setting up vtest data
        test_json_object = {
            'type': 'test',
            'source': video_obj['source'],
            'eng_text': video_obj['eng_text'],
            'ru_text': video_obj['ru_text'],
            'tip': video_obj['tip'],
            'server_choices': choices,
        }  

        # Final setting Videotest data to craft
        craft.append(test_json_object)

    # Iterate one more time to craft sentence parts
    for video_obj in valid_json_video_objects:
        # Craft cards
        part_json_object = {
            'type': 'part',
            'source': video_obj['source'],
            'eng_text': video_obj['eng_text'],
            'ru_text': video_obj['ru_text'],
            'tip': video_obj['tip'],
        }

        # append result of crafted parts
        craft.append(part_json_object)

    return JsonResponse(craft, safe=False)

# Save passed course 

def save_learned_subcourse(request):
    # get users token from post cause of secure
    token = request.POST['token']
    # Handle user settings by token
    user_settings = UserSettings.objects.get(user_token=token)
    # Get current subcourse by its id
    subcourse_id = request.POST['subcourse_id']
    # Handle subcourse object by id
    sub_course = SubCourse.objects.get(id=subcourse_id)

    # Assign subcourse to user settings
    user_settings.learned_courses.add(sub_course)
    user_settings.save()

    return HttpResponse('Query complete!')

