import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.http import JsonResponse

from django.shortcuts import render


from financew.models import Budget, FinOperation, Category

    

def visualisation(request):
    """Сторінка візуалізації"""
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.filter(owner=request.user)
    finoperations = FinOperation.objects.filter(budget__owner=request.user)
    
    # Перетворюємо результат запиту в DataFrame
    df = pd.DataFrame(list(finoperations.values( 'amount', 'type', 'category__name')))
    
    # Переглянути перші кілька рядків таблиці
    print(df.head())
    
    selected_type = request.GET.get('type', None)
    # Фільтруємо за типом операції, якщо параметр задано
    if selected_type:
        df = df[df['type'] == selected_type]

    df_grouped = df.groupby(['category__name'])['amount'].sum().reset_index()
    print(df_grouped.head())
    # fig = px.pie(ЯКЕСЬ DF, values='expenes', names='category', title='Population of European continent')
    
    fig = px.pie(df_grouped, 
            #  names='type',  # Імена категорій
             values='amount',         # Значення для pie chart (суми)
             color='category__name',            # Розрізняємо по типу операції (income або expense)
             title='Розподіл фінансових операцій за категоріями та типами',
             )
    

    graph_html = fig.to_html(full_html=False)

    context = { 'budgets':budgets,
                'categories':categories,
                'finoperations':finoperations,
                'graph': graph_html,
                
    }
    return render(request, "plots/report.html", context)


    # # Всі фінансові операції
    # budgets = Budget.objects.all()
    # data_options = {
    #     'time_intervals': {
    #     "one_time": "Одноразовий",
    #     "weekly": "Щотижня",
    #     "monthly": "Щомісяця",
    #     "annually": "Щорічно",
    # }
    # }

    # # Отримання вибраного інтервалу
    # selected_interval = request.GET.get("time_interval", "one_time")

    # # Обробка даних
    # data = []
    # for budget in budgets:
    #     operations = budget.finoperation_set.filter(time_interval=selected_interval).order_by("date_added")
    #     net_income = 0  # Чистий прибуток
    #     for op in operations:
    #         if op.type == "income":
    #             net_income += op.amount
    #         else:
    #             net_income -= op.amount
            
    #         data.append({
    #             "Дата": op.date_added.strftime('%Y-%m-%d'),
    #             "Сума": net_income,
    #             "Тип": "Прибуток" if net_income >= 0 else "Витрати"
    #         })

    # # Перетворення у DataFrame
    # df = pd.DataFrame(data)
    # if not df.empty:
    #     fig = px.line(
    #         df, x="Дата", y="Сума", color="Тип", title=f"Динаміка ({data_options['time_intervals'][selected_interval]})", markers=True,
    #         color_discrete_map={"Прибуток": "blue", "Витрати": "red"}  # Червоний для витрат, синій для прибутку
    #     )
    #     fig.update_traces(marker=dict(size=8), line=dict(width=2))
    #     fig.update_layout(xaxis_title='Дата', yaxis_title='Сума')
    #     plot_html = fig.to_html(full_html=False)
    # else:
    #     plot_html = "<p>Недостатньо даних для візуалізації.</p>"

    # context = {
    #     'plot_html': plot_html,
    #     'data_options': data_options,
    #     'selected_interval': selected_interval
    # }
    # return render(request, "plots/report.html", context)


    # user = request.user
    # operations = FinOperation.objects.filter(budget__owner=user, type='expense')  # тільки витрати
    # categories = operations.values('category__name').distinct()

    # category_data = {}

    # for category in categories:
    #     category_name = category['category__name']
    #     total_expense = operations.filter(category__name=category_name).aggregate(total=models.Sum('amount'))['total']
    #     category_data[category_name] = total_expense or 0  # якщо немає витрат по категорії, то 0

    # return JsonResponse(category_data)