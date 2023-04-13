from django.contrib import admin
from django.urls import path

from .views import  Search

urlpatterns = [

    # todo: add home page
    path('search-hashtag/', Search.as_view(), name='search_hashtag'),

]