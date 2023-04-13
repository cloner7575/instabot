from django.contrib import admin
from django.urls import path

from .views import  Search,index

urlpatterns = [


    path('', index, name='home'),
    path('search-hashtag/', Search.as_view(), name='search_hashtag'),

]