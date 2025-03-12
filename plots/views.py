import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import render
import random

from financew.constants import FINOPERATION_TYPE
from financew.models import Budget, FinOperation, Category
from .forms import FinOperationTypeForm, WhichBudgetForm

def visualisation(request):
    """Сторінка візуалізації"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    """форма для фін операцій"""
    finoperation_type = request.GET.get('finoperation_type', request.session.get('finoperation_type', random.choice(list(FINOPERATION_TYPE.keys())))) # вибираємо на рандом
    finoperationtypeform = FinOperationTypeForm(initial={'finoperation_type': finoperation_type})
    selected_finoperation_type = request.GET.get('finoperation_type', None) # None якщо нічого не вибрано
    if selected_finoperation_type:
        request.session['finoperation_type'] = selected_finoperation_type
    
    """форма для вибору бюджету"""
    budget_type = request.GET.get('budget_type', request.session.get('budget_type', 'all')) # вибираємо на рандом
    budgetform = WhichBudgetForm(initial={'budget_type': budget_type},user = request.user,)
    selected_budget_type = request.GET.get('budget_type', None) # None якщо нічого не вибрано
    print(selected_budget_type)
    if selected_finoperation_type:
        request.session['budget_type'] = selected_budget_type
    
    
    
    # # Перетворюємо результат запиту в DataFrame
    # df = pd.DataFrame(list(finoperations.values( 'amount', 'type', 'category__name')))
    
    # # Переглянути перші кілька рядків таблиці
    # print(df.head())
    
    # selected_type = request.GET.get('type', None)
    # # Фільтруємо за типом операції, якщо параметр задано
    # if selected_type:
    #     df = df[df['type'] == selected_type]

    # df_grouped = df.groupby(['category__name'])['amount'].sum().reset_index()
    # print(df_grouped.head())
    # # fig = px.pie(ЯКЕСЬ DF, values='expenes', names='category', title='Population of European continent')
    
    # fig = px.pie(df_grouped, 
    #         #  names='type',  # Імена категорій
    #          values='amount',         # Значення для pie chart (суми)
    #          color='category__name',            # Розрізняємо по типу операції (income або expense)
    #          title='Розподіл фінансових операцій за категоріями та типами',
    #          )
    

    # graph_html = fig.to_html(full_html=False)

    context = { 'budgets':budgets,
                'categories':categories,
                'finoperations':finoperations,
                # 'display_finoperation_type':display_finoperation_type,
                'finoperationtypeform':finoperationtypeform,
                # 'graph': graph_html,
                'budgetform':budgetform,
                
    }
    return render(request, "plots/report.html", context)

def get_pie_chart_data(request):
    """дані для кругової діаграми та отримання фінансових даних у JSON"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)

    
    
    df = pd.DataFrame(list(finoperations.values('amount', 'type', 'category__name')))# Перетворюємо в DataFrame
    # print(finoperations)
    if df.empty:
        return JsonResponse({"labels": [], "values": []})  # Якщо немає даних

    #Отримання типу фін операції
    selected_type = request.session.get('finoperation_type', None) # беремо це діло через сесію
    print(selected_type)
    if selected_type:
        df = df[df['type'] == selected_type]

    df_grouped = df.groupby(['category__name'])['amount'].sum().reset_index()

    data = {
        "labels": df_grouped['category__name'].tolist(),
        "values": df_grouped['amount'].tolist(),
    }

    return JsonResponse(data)