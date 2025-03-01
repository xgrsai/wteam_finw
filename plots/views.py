import pandas as pd
import plotly.express as px
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
import pandas as pd
from financew.models import Budget, GoalBudget, FinOperation  # Імпорт моделей з financew

def visualisation(request):
    """Сторінка візуалізації з вибором інтервалу часу"""

    # Всі фінансові операції
    budgets = Budget.objects.all()
    data_options = {
        'time_intervals': {
            "one_time": "Одноразовий",
            "weekly": "Щотижня",
            "monthly": "Щомісяця",
            "annually": "Щорічно",
    }
    }

    # Отримання вибраного інтервалу
    selected_interval = request.GET.get("time_interval", "monthly")

    # Обробка даних
    data = []
    for budget in budgets:
        operations = budget.finoperation_set.filter(time_interval=selected_interval).order_by("date_added")
        net_income = 0  # Чистий прибуток
        for op in operations:
            if op.type == "income":
                net_income += op.amount
            else:
                net_income -= op.amount
            
            data.append({
                "Дата": op.date_added.strftime('%Y-%m-%d'),
                "Сума": net_income,
                "Тип": "Прибуток" if net_income >= 0 else "Витрати"
            })

    # Перетворення у DataFrame
    df = pd.DataFrame(data)
    if not df.empty:
        fig = px.line(
            df, x="Дата", y="Сума", color="Тип", title=f"Динаміка ({data_options['time_intervals'][selected_interval]})", markers=True,
            color_discrete_map={"Прибуток": "blue", "Витрати": "red"}  # Червоний для витрат, синій для прибутку
        )
        fig.update_traces(marker=dict(size=8), line=dict(width=2))
        fig.update_layout(xaxis_title='Дата', yaxis_title='Сума')
        plot_html = fig.to_html(full_html=False)
    else:
        plot_html = "<p>Недостатньо даних для візуалізації.</p>"

    context = {
        'plot_html': plot_html,
        'data_options': data_options,
        'selected_interval': selected_interval
    }
    return render(request, "visual/visual.html", context)





def budget_chart(request):
    """Сторінка з графіками бюджетів, бюджетів-цілей та фінансових операцій"""

    # Отримуємо всі бюджети, бюджети-цілі та фінансові операції для поточного користувача
    budgets = Budget.objects.filter(owner=request.user)
    goal_budgets = GoalBudget.objects.filter(owner=request.user)
    fin_operations = FinOperation.objects.filter(budget__owner=request.user)

    # Створюємо DataFrame для графіку бюджетів
    budget_data = {
        'Назва бюджету': [budget.name for budget in budgets],
        'Сума': [float(budget.amount) for budget in budgets],  # Перетворюємо Decimal на float
        'Валюта': [budget.currency for budget in budgets]
    }
    budget_df = pd.DataFrame(budget_data)

    # Створюємо стовпчастий графік для бюджетів
    if not budget_df.empty:
        budget_fig = px.bar(budget_df, x='Назва бюджету', y='Сума', color='Валюта', title='Графік бюджетів')
        budget_plot_html = budget_fig.to_html(full_html=False)
    else:
        budget_plot_html = "<p>Немає даних для відображення графіку бюджетів.</p>"

    # Створюємо DataFrame для графіку бюджетів-цілей
    goal_budget_data = {
        'Назва бюджету-цілі': [goal.name for goal in goal_budgets],
        'Поточна сума': [float(goal.amount) for goal in goal_budgets],  # Перетворюємо Decimal на float
        'Цільова сума': [float(goal.target_amount) for goal in goal_budgets],  # Перетворюємо Decimal на float
        'Валюта': [goal.currency for goal in goal_budgets]
    }
    goal_budget_df = pd.DataFrame(goal_budget_data)

    # Створюємо стовпчастий графік для бюджетів-цілей
    if not goal_budget_df.empty:
        goal_budget_fig = px.bar(goal_budget_df, x='Назва бюджету-цілі', y=['Поточна сума', 'Цільова сума'], 
                                title='Графік бюджетів-цілей', barmode='overlay',
                                color_discrete_map={
                                    'Поточна сума': 'blue',  # Колір для "Поточної суми"
                                    'Цільова сума': 'green'  # Колір для "Цільової суми"
                                })
        goal_budget_plot_html = goal_budget_fig.to_html(full_html=False)
    else:
        goal_budget_plot_html = "<p>Немає даних для відображення графіку бюджетів-цілей.</p>"

    # Створюємо DataFrame для графіку фінансових операцій
    fin_operation_data = {
        'Категорія': [operation.category.name if operation.category else "Без категорії" for operation in fin_operations],
        'Сума': [float(operation.amount) for operation in fin_operations],  # Перетворюємо Decimal на float
        'Тип операції': [operation.type for operation in fin_operations],
        'Валюта': [operation.budget.currency for operation in fin_operations]
    }
    fin_operation_df = pd.DataFrame(fin_operation_data)

    # Створюємо круговий графік для фінансових операцій
    if not fin_operation_df.empty:
        fin_operation_fig = px.pie(fin_operation_df, names='Категорія', values='Сума', 
                                   title='Розподіл фінансових операцій за категоріями')
        fin_operation_plot_html = fin_operation_fig.to_html(full_html=False)
    else:
        fin_operation_plot_html = "<p>Немає даних для відображення графіку фінансових операцій.</p>"

    # Передаємо всі графіки у шаблон
    context = {
        'budget_plot_html': budget_plot_html,
        'goal_budget_plot_html': goal_budget_plot_html,
        'fin_operation_plot_html': fin_operation_plot_html,
    }

    return render(request, 'financew/my.html', context)

