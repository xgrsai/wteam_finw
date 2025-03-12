import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.http import JsonResponse
from django.shortcuts import render
import random

from .constants import GRAPH_TYPE_CHOICES
from financew.constants import FINOPERATION_TYPE
from financew.models import Budget, FinOperation, Category
from .forms import FinOperationTypeForm, WhichBudgetForm, GraphicTypeForm

def visualisation(request):
    """Сторінка візуалізації"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    ###ФОРМА ЯКИЙ ГРАФІК ОБРАТИ###
    graphic_type = request.GET.get('graphic_type', request.session.get('graphic_type', random.choice(list(GRAPH_TYPE_CHOICES.keys()))))
    graphic_type_form = GraphicTypeForm(initial={'graphic_type': graphic_type})
    selected_graphic_type = request.GET.get('graphic_type', None) # None якщо нічого не вибрано
    if selected_graphic_type:
        request.session['graphic_type'] = selected_graphic_type

    ###ФІЛЬТРИ ГРАФІК PIECHART###
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
    if selected_finoperation_type:
        request.session['budget_type'] = selected_budget_type

    ###ГРАФІК BARCHART###


    context = { 'budgets':budgets,
                'categories':categories,
                'finoperations':finoperations,
                # 'display_finoperation_type':display_finoperation_type,
                'finoperationtypeform':finoperationtypeform,
                # 'graph': graph_html,
                'budgetform':budgetform,
                'graphic_type_form':graphic_type_form,
                'graphic_type':graphic_type,
                
    }
    return render(request, "plots/report.html", context)

def get_pie_chart_data(request):
    """дані для кругової діаграми та отримання фінансових даних у JSON"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)

    """для вибору бюджету"""
    budget_type = request.session.get('budget_type')
    if budget_type == 'all':
        df = pd.DataFrame(list(finoperations.values('amount', 'type', 'category__name')))# Перетворюємо в DataFrame
    else:
        df = pd.DataFrame(list(finoperations.filter(budget=budget_type).values('amount', 'type', 'category__name')))# Перетворюємо в DataFrame
    
    # print(finoperations)
    if df.empty:
        return JsonResponse({"labels": [], "values": []})  # Якщо немає даних

    """фільтр типу фіноперації"""
    selected_type = request.session.get('finoperation_type') # беремо це діло через сесію
    if selected_type:
        df = df[df['type'] == selected_type]

    df_grouped = df.groupby(['category__name'])['amount'].sum().reset_index() # 1) df.groupby(['category__name']): Це групує DataFrame df за значеннями в стовпці category__name. Тобто, всі записи з однаковим значенням в колонці category__name будуть об'єднані в одну групу. 2) ['amount']: Після того як дані будуть згруповані за категоріями, вибирається стовпець amount, в якому буде обчислюватися сума для кожної групи. 3) .sum(): Цей метод застосовується до кожної групи, обчислюючи суму значень у стовпці amount для кожної категорії. 4) .reset_index(): Після групування і обчислення суми, цей метод відновлює індекси DataFrame (по суті, створює новий DataFrame з індексами, починаючи з 0, замість того, щоб залишати їх у вигляді багаторівневих індексів після групування).

    data = {
        "labels": df_grouped['category__name'].tolist(),
        "values": df_grouped['amount'].tolist(),
    }

    return JsonResponse(data)


def get_bar_chart_data(request):
    """дані для barchart"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    """для вибору бюджету"""
    budget_type = request.session.get('budget_type')
    if budget_type == 'all':
        df = pd.DataFrame(list(finoperations.values('amount', 'type', 'category__name')))# Перетворюємо в DataFrame
    else:
        df = pd.DataFrame(list(finoperations.filter(budget=budget_type).values('amount', 'type', 'category__name')))# Перетворюємо в DataFrame
    
    # print(finoperations)
    if df.empty:
        return JsonResponse({"labels": [], "values": []})  # Якщо немає даних

    """фільтр типу фіноперації"""
    selected_type = request.session.get('finoperation_type') # беремо це діло через сесію
    if selected_type:
        df = df[df['type'] == selected_type]

    df_grouped = df.groupby(['category__name'])['amount'].sum().reset_index() # 1) df.groupby(['category__name']): Це групує DataFrame df за значеннями в стовпці category__name. Тобто, всі записи з однаковим значенням в колонці category__name будуть об'єднані в одну групу. 2) ['amount']: Після того як дані будуть згруповані за категоріями, вибирається стовпець amount, в якому буде обчислюватися сума для кожної групи. 3) .sum(): Цей метод застосовується до кожної групи, обчислюючи суму значень у стовпці amount для кожної категорії. 4) .reset_index(): Після групування і обчислення суми, цей метод відновлює індекси DataFrame (по суті, створює новий DataFrame з індексами, починаючи з 0, замість того, щоб залишати їх у вигляді багаторівневих індексів після групування).

    data = {
        "labels": df_grouped['category__name'].tolist(),
        "values": df_grouped['amount'].tolist(),
    }

    return JsonResponse(data)