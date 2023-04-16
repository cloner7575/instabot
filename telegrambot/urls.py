from django.urls import path

from . import views

urlpatterns = [
    path('save_contacts/', views.save_contacts, name='save_contacts'),


]