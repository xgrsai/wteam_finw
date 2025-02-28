from django.urls import path
from . import views

app_name = "plots"
urlpatterns = [
    #Головна сторінка
    path("", views.visualisation, name="report"),
]