from django.contrib import admin
from django.urls import path

from .views import  Search,index,AccountInfoResult

urlpatterns = [


    path('', index, name='home'),
    path('search-hashtag/', Search.as_view(), name='search_hashtag'),
    path('account_info_result/', AccountInfoResult.as_view(), name='account_info_result'),

]