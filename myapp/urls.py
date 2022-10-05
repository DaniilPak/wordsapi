
from django.urls import path

from . import views

urlpatterns = [
    path('<str:token>', views.index, name='index'),
    path('reguser/new', views.register_new_user, name='reguser'),
    path('my/saveword', views.save_learned_words, name='saveword'),
    path('my/word', views.my_word, name='myword'),
    path('my/repeat', views.repeat_words, name='repeat'),
    path('my/hard', views.hard_word, name='hard'),
    path('my/changelevel', views.change_level, name='changelevel'),
    path('my/changetopic', views.change_topic, name='changetopic'),
    path('my/topic', views.get_users_topic, name='usertopic'),
    path('my/level', views.get_users_level, name='userlevel'),
    path('misc/dummy', views.get_dummy, name='getdummy'),
    path('my/wordscount', views.get_users_my_words_amount, name='mywordsamount'),
    path('my/repeatwordscount', views.get_users_repeat_words_amount, name='mywordsamount'),
    path('my/hardwordscount', views.get_users_hard_words_amount, name='mywordsamount'),
    path('my/renewrepeatwords', views.renew_repeated_words, name='renewrepeatwords'),
    path('my/detecthardwords', views.detect_hard_words, name='detecthardwords'),
    path('my/deletehardwords', views.delete_hard_words, name='deletehardwords'),
    
    # path('loadwords', views.loadwords, name='loadwords'),

    ### COURSES ###
    path('courses/english', views.index_courses, name='courses'),
    path('courses/english/craft/<int:craft_id>', views.get_craft, name='courses_craft'),
]
