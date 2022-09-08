from cgitb import text
from django.shortcuts import render
from .models import *

# Import to process
# django data to JSON
import requests
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
from django.db.models import Q

# Hash 256
from hashlib import sha256

# Create your views here.

def index(request):
    # This filteres words that are already on learning
    # ~ has a mirroring effect
    filtered_oxs = OxfordWord.objects.filter(~Q(id__in=[o for o in [0]]))

    # items = list(OxfordWord.objects.filter(CEFR='A2', topic='Work and business'))
    items = list(filtered_oxs.filter(CEFR='A1', topic='People'))

    # change 3 to how many random items you want
    # Deprecated code, don't need to take random ones
    # instead taking first [amount of words] used
    # words_taken_from_api = random.sample(items, 5)

    # change num to take exact amount
    words_taken_from_api = items[:5] 

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

        fixed_oxford_words.append(item['fields'])

    # Final deploy
    context = {
        'data': json.dumps(fixed_oxford_words)
    }

    return render(request, 'myapp/index.html', context)

# Register, Login, Saving Progress

def register_new_user(request):
    
    # Getting POSTed data
    email = request.GET['email']
    password = request.GET['password']

    # concat email & pass to create a sha256
    input_ = email + password

    # Generate token 
    user_token = sha256(input_.encode('utf-8')).hexdigest()

    # Create UserSettings and set user token
    user_settings = UserSettings(user_token=user_token)
    user_settings.save()

    # Giving user_token to user
    user_token_list = {
        'user_token': user_token
    }

    context = {
        'user_token_list': json.dumps(user_token_list),
    }

    return render(request, 'myapp/get_user_token.html', context)

'''
def loadwords(request):

    # Constants
    filename = 'data.csv'

    app_id = '67e81b64'
    app_key = 'b7e2a6a71759b353377da065a42998cd'
    with open(filename, 'r') as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:

            # Translate call
            url = "https://od-api.oxforddictionaries.com:443/api/v2/translations/en/ru/" + row[0]
            r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
            json_data = json.loads(r.content)

            # Data call
            url_dc = "https://od-api.oxforddictionaries.com:443/api/v2/words/en-us?q=" + row[0]
            r_dc = requests.get(url_dc, headers={"app_id": app_id, "app_key": app_key})
            json_data_dc = json.loads(r_dc.content)

            # Check if word exists
            if 'results' in json_data and 'results' in json_data_dc and 'senses' in json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0] and 'definitions' in json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0] and 'translations' in json_data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0] and 'pronunciations' in json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]:
            # mp3 saving process
                if 'pronunciations' in json_data['results'][0]['lexicalEntries'][0]['entries'][0]:
                    url_gb = json_data['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['audioFile']
                    gb_mp3_filename = str(url_gb).rsplit('/', 1)[1]
                    gb_mp3_request = requests.get(url_gb, allow_redirects=True)
                    open('media/' + gb_mp3_filename, 'wb').write(gb_mp3_request.content)

                    # mp3 second saving for us
                    url_us = json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]['audioFile']
                    us_mp3_filename = str(url_us).rsplit('/', 1)[1]
                    us_mp3_request = requests.get(url_us, allow_redirects=True)
                    open('media/' + us_mp3_filename, 'wb').write(us_mp3_request.content)

                    oword = OxfordWord.objects.create(
                        # T
                        word = json_data['results'][0]['word'],
                        translate_ru = json_data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['translations'][0]['text'],
                        pronunciation_gb = gb_mp3_filename,
                        spelling_gb = json_data['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][0]['phoneticSpelling'],
                        lexical_category = json_data['results'][0]['lexicalEntries'][0]['lexicalCategory']['text'],
                        CEFR = '', # Change #########################################################################
                        topic = '', ###############################################################
                        # W
                        pronunciation_us = us_mp3_filename,
                        spelling_us = json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['pronunciations'][1]['phoneticSpelling'],
                        definition = json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
                    )

                    # Adding examples
                    if 'examples' in json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]:
                        jsonStr = json.dumps(json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['examples'])
                        aList = json.loads(jsonStr)

                        for ex in aList:
                            oxex = OxExample.objects.create(text = ex['text'])
                            oxex.save()
                            oword.examples.add(oxex)

                    # Adding inflections
                    if 'inflections' in json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]:
                        jsonStr2 = json.dumps(json_data_dc['results'][0]['lexicalEntries'][0]['entries'][0]['inflections'])
                        aList2 = json.loads(jsonStr2)

                        for inf in aList2:
                            new_inf = Inflection.objects.create(text = inf['inflectedForm'])
                            new_inf.save()
                            oword.inflections.add(new_inf)

    context = {
        'data': 'Done!'
    }

    return render(request, 'myapp/index.html', context)
'''