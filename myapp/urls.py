
from django.urls import path

from . import views

urlpatterns = [
    path('<str:token>', views.index, name='index'),
    path('reguser/new', views.register_new_user, name='reguser'),
    path('my/saveword', views.save_learned_words, name='saveword'),
    # path('loadwords', views.loadwords, name='loadwords'),
]
