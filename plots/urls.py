from django.urls import path
from . import views

app_name = "plots"
urlpatterns = [
    #Головна сторінка
    path("", views.visualisation, name="report"),
    path("get_pie_chart_data/", views.get_pie_chart_data, name="piechart-data"),
    path("get_bar_chart_data/", views.get_bar_chart_data, name="barchart-data"),
]