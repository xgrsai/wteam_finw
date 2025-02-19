"""Ввзначає URL шаблони для financew"""

from django.urls import path

from . import views

app_name = "financew"
urlpatterns = [
    #Головна сторінка
    path("", views.index, name='index'),

]