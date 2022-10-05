from cgitb import text
from django.http import HttpResponse
from unicodedata import name
from django.shortcuts import render
from .models import *

# Import to process
# django data to JSON
# import requests
import json

# Used to load words
import csv

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
    user_settings = UserSettings(user_token=user_token)
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

    context = {
        'user_token_list': json.dumps(user_token_list),
    }

    return render(request, 'myapp/get_user_token.html', context)

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

    # Handle learned words
    learned_words = user_settings.learned_words.all()

    # Iterate over learned words to create array with only ids
    ids = []
    for lw in learned_words:
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

    # change num to take exact amount
    words_taken_from_api = random.sample(items, 10)

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)

# This view gets learned words 
# and sets to UserSettings accountant

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_topics)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(fixed_levels)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(arr_for_deploy)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(arr_for_deploy)
    }

    return render(request, 'myapp/index.html', context)

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

    # Final deploy
    context = {
        'data': json.dumps(arr_for_deploy)
    }

    return render(request, 'myapp/index.html', context)


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

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)





### COURSES ###

# API for courses & videotests(videocards)

def index_courses(request):
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

        # Saving all processed data to future json object
        courses_fixed_json.append(item['fields'])
 
    context = {
        'data': json.dumps(courses_fixed_json),
    }
    return render(request, 'myapp/index.html', context)


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
    for video_obj in valid_json_video_objects:
        # Handling server choice 1
        server_choice_1_obj = ServerChoice.objects.get(id=video_obj['server_choice_1'])
        # Fixint to JSON representation
        server_choice_1_json = serializers.serialize('python', [server_choice_1_obj])

        # Handling server choice 2
        server_choice_2_obj = ServerChoice.objects.get(id=video_obj['server_choice_2'])
        # Fixint to JSON representation
        server_choice_2_json = serializers.serialize('python', [server_choice_2_obj])

        # Handling server choice 3
        server_choice_3_obj = ServerChoice.objects.get(id=video_obj['server_choice_3'])
        # Fixint to JSON representation
        server_choice_3_json = serializers.serialize('python', [server_choice_3_obj])

        # Handling server choice 2
        server_choice_4_obj = ServerChoice.objects.get(id=video_obj['server_choice_4'])
        # Fixint to JSON representation
        server_choice_4_json = serializers.serialize('python', [server_choice_4_obj])

        # Setting up vtest data
        test_json_object = {
            'type': 'test',
            'source': video_obj['source'],
            'eng_text': video_obj['eng_text'],
            'ru_text': video_obj['ru_text'],
            'tip': video_obj['tip'],
            'server_choice_1': server_choice_1_json[0]['fields'],
            'server_choice_2': server_choice_2_json[0]['fields'],
            'server_choice_3': server_choice_3_json[0]['fields'],
            'server_choice_4': server_choice_4_json[0]['fields'],
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

    context = {
        'data': json.dumps(craft),
    }

    return render(request, 'myapp/index.html', context)