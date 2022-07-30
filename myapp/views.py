from cgitb import text
from django.shortcuts import render
from .models import *

import requests
import json

import csv

import random

# Create your views here.

def index(request):

    items = list(OxfordWord.objects.filter(CEFR='B2'))

    # change 3 to how many random items you want
    random_items = random.sample(items, 20)

    context = {
        'data': random_items
    }

    return render(request, 'myapp/index.html', context)

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