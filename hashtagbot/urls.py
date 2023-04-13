from django.contrib import admin
from django.urls import path

from .views import  Search,index

urlpatterns = [

    # todo: add home page
    path('', index, name='home'),
    path('search-hashtag/', Search.as_view(), name='search_hashtag'),

]