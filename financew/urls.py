"""Ввзначає URL шаблони для financew"""

# from django.urls import path
from django.urls import path, include
from . import views

app_name = "financew"
urlpatterns = [
    path("", views.index, name='index'),
    path("my/", views.my, name='my'), #особистий кабінет
    path("budget/<int:budget_id>/", views.budget, name='budget'), # сторінка з бюджетами
    path("new_finoperation/<int:budget_id>/", views.new_finoperation, name='new_finoperation'),
    path("budget/<int:budget_id>/", views.budget, name='budget'),
    path("new_finoperation/<int:budget_id>/", views.new_finoperation, name='new_finoperation'),
    path("delete_finoperation/<int:finoperation_id>/", views.delete_finoperation, name='delete_finoperation'),
    path("edit_budget/<int:budget_id>/", views.edit_budget, name='edit_budget'),
    path("edit_finoperation/<int:finoperation_id>/", views.edit_finoperation, name='edit_finoperation'),
]


