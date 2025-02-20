"""Ввзначає URL шаблони для financew"""

from django.urls import path

from . import views

app_name = "financew"
urlpatterns = [
    #Головна сторінка
    path("", views.index, name='index'),
    path("budgets/<int:budget_id>/", views.budget, name='budget'), # сторінка з бюджетами
    path("new_finoperation/<int:budget_id>/", views.new_finoperation, name='new_finoperation'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]