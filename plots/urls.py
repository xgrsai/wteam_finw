from django.urls import path
from . import views

app_name = "plots"
urlpatterns = [
    #Головна сторінка
    path("report/", views.some, name='report'),
]