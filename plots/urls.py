from django.urls import path

from . import views

from .views import visualisation
from plots.views import budget_chart  # Імпорт з plots

app_name = "plots"
urlpatterns = [
    #Головна сторінка

    path("visualisation/", visualisation, name='visualisation'),
    path('budget_chart/', budget_chart, name='budget_chart'),  # Шлях для графіків

]