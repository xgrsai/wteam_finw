import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
import random

from .constants import GRAPH_TYPE_CHOICES
from financew.constants import FINOPERATION_TYPE
from financew.models import Budget, FinOperation, Category
from .forms import FinOperationTypeForm, WhichBudgetForm, GraphicTypeForm
from financew.forms import CurrencyForm
from .utils import convert_df_amount

def visualisation(request):
    """Сторінка візуалізації"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    """форма для вибору яку валюту відобразити"""
    display_currency = request.GET.get('currency', request.session.get('display_currency', 'UAH'))# Отримуємо валюту з сесії (якщо є), або використовуємо дефолтну 'UAH'
    currencydisplayform = CurrencyForm(initial={'currency': display_currency}) # Створюємо форму з ініціалізацією значення за замовчуванням
    selected_currency = request.GET.get('currency', None) # None якщо нічого не вибрано
    if selected_currency:
        request.session['display_currency'] = selected_currency # Якщо валюта вибрана, зберігаємо її в сесії

    ###ФОРМА ЯКИЙ ГРАФІК ОБРАТИ###
    graphic_type = request.GET.get('graphic_type', request.session.get('graphic_type', random.choice(list(GRAPH_TYPE_CHOICES.keys()))))
    graphic_type_form = GraphicTypeForm(initial={'graphic_type': graphic_type})
    selected_graphic_type = request.GET.get('graphic_type', None) # None якщо нічого не вибрано
    if selected_graphic_type:
        request.session['graphic_type'] = selected_graphic_type

    ###ФІЛЬТРИ###
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
    if selected_budget_type:
        request.session['budget_type'] = selected_budget_type

    ###context###
    context = { 'budgets':budgets,
                'categories':categories,
                'finoperations':finoperations,
                'finoperationtypeform':finoperationtypeform,
                'budgetform':budgetform,
                'graphic_type_form':graphic_type_form,
                'graphic_type':graphic_type,
                'currencydisplayform':currencydisplayform,
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
        df = pd.DataFrame(list(finoperations.values('amount', 'type', 'category__name', 'budget__currency')))# Перетворюємо в DataFrame
    else:
        df = pd.DataFrame(list(finoperations.filter(budget=budget_type).values('amount', 'type', 'category__name','budget__currency')))# Перетворюємо в DataFrame
    if df.empty:
        return JsonResponse({"labels": [], "values": []})  # Якщо немає даних

    """перетворення None на 'без категорії'"""
    df['category__name'] = df['category__name'].fillna("Без категорії") # спеціальний метод для заповнення пустих значень

    """Переведення за вибраною валютою"""
    selected_currency = request.session.get('display_currency')
    
    df = convert_df_amount(df, selected_currency)

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
    """Дані для barchart"""
    # Отримуємо всі бюджети, навіть ті, у яких немає фінансових операцій
    budgets = Budget.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    # Для вибору бюджету
    budget_type = request.session.get('budget_type')

    if budget_type == 'all':
        df = pd.DataFrame(list(finoperations.values('amount', 'type', 'budget__name','budget__currency','category__name')))  # Перетворюємо в DataFrame
    else:
        df = pd.DataFrame(list(finoperations.filter(budget=budget_type).values('amount', 'type', 'budget__name', 'budget__currency','category__name')))  # Перетворюємо в DataFrame
    
    """перетворення None на 'без категорії'"""
    df['category__name'] = df['category__name'].fillna("Без категорії") # спеціальний метод для заповнення пустих значень

    """зміна валюти"""
    selected_currency = request.session.get('display_currency')
    df = convert_df_amount(df, selected_currency)
    
    # Фільтруємо дані по прибутку та витратах
    df_profit = df[df['type'] == 'income']  # Прибуток
    df_expenses = df[df['type'] == 'expense']  # Витрати
    
    # Групуємо за кожним бюджетом для прибутку та витрат
    df_profit_grouped = df_profit.groupby('budget__name')['amount'].sum().reset_index()
    df_expenses_grouped = df_expenses.groupby('budget__name')['amount'].sum().reset_index()
    
    # Використовуємо merge, щоб з'єднати дві таблиці
    df_combined = pd.merge(df_profit_grouped, df_expenses_grouped, on='budget__name', how='left', suffixes=('_profit', '_expenses'))
    
      # Використовуємо merge, щоб з'єднати дві таблиці
    df_combined = pd.merge(df_profit_grouped, df_expenses_grouped, on='budget__name', how='left', suffixes=('_profit', '_expenses'))
    
    # Заповнюємо пропущені значення 0 для витрат і прибутку
    df_combined['amount_profit'] = df_combined['amount_profit'].fillna(0)
    df_combined['amount_expenses'] = df_combined['amount_expenses'].fillna(0)

    # Формуємо фінальний результат
    data = {
         "labels": df_combined['budget__name'].tolist(),  # Лейбли - бюджети
         "profit": df_combined['amount_profit'].tolist(),  # Суми прибутку
         "expenses": df_combined['amount_expenses'].tolist(),  # Суми витрат
     }
    
    return JsonResponse(data)

def get_line_chart_data(request):
    """Дані для лінійного графіка по датах"""
    
    # Фільтруємо фінансові операції для поточного користувача
    finoperations = FinOperation.objects.filter(budget__owner=request.user)

    # Перевірка на тип бюджету (якщо потрібно)
    budget_type = request.session.get('budget_type')
    if budget_type == 'all':
        df = pd.DataFrame(list(finoperations.values('amount', 'type', 'date_added', 'budget__currency','category__name')))  # Перетворюємо в DataFrame
    else:
        df = pd.DataFrame(list(finoperations.filter(budget=budget_type).values('amount', 'type', 'date_added','budget__currency','category__name')))  # Перетворюємо в DataFrame
    # Якщо дані відсутні
    if df.empty:
        return JsonResponse({"labels": [], "profit": [], "expenses": []})

    """перетворення None на 'без категорії'"""
    df['category__name'] = df['category__name'].fillna("Без категорії") # спеціальний метод для заповнення пустих значень

    """зміна валюти"""
    selected_currency = request.session.get('display_currency')
    df = convert_df_amount(df, selected_currency)

    # Додаємо колонку з датами (можна форматувати дату для групування)
    df['date_added'] = pd.to_datetime(df['date_added']).dt.date  # Залишаємо тільки дату без часу

    # Групуємо за датами та типами операцій (прибуток або витрати)
    df_profit = df[df['type'] == 'income'].groupby('date_added')['amount'].sum().reset_index()  # Прибуток
    df_expenses = df[df['type'] == 'expense'].groupby('date_added')['amount'].sum().reset_index()  # Витрати
    
    # Об'єднуємо дані
    all_dates = pd.date_range(start=df['date_added'].min(), end=df['date_added'].max()).date  # Створюємо список всіх дат від мінімальної до максимальної
    
    df_profit = df_profit.set_index('date_added').reindex(all_dates, fill_value=0).reset_index()  # Заповнюємо пропущені дати для прибутку
    df_expenses = df_expenses.set_index('date_added').reindex(all_dates, fill_value=0).reset_index()  # Заповнюємо пропущені дати для витрат

    # Підготовка даних для відповіді
    data = {
        "labels": df_profit['date_added'].astype(str).tolist(),  # Перетворюємо дати на строки для відображення
        "profit": df_profit['amount'].tolist(),  # Дані по прибутку
        "expenses": df_expenses['amount'].tolist(),  # Дані по витратах
    }
    
    return JsonResponse(data)