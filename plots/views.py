import pandas as pd
import plotly.express as px
from django.shortcuts import render
from financew.models import Budget, FinOperation

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
