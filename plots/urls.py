from django.urls import path

from . import views

from .views import visualisation

app_name = "plots"
urlpatterns = [
    #Головна сторінка

    path("visualisation/", visualisation, name='visualisation'),


]