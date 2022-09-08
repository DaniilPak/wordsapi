
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reguser', views.register_new_user, name='reguser'),
    # path('loadwords', views.loadwords, name='loadwords'),
]