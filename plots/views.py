from django.shortcuts import render

import plotly.express as px
import pandas as pd

def visualisation(request):
    """Сторінка візуалізації з вибором категорій"""

    # Дані для вибору категорій
    data_options = {
        'x': {
            'x1': [1, 2, 3, 4],
            'x2': [10, 20, 30, 40]
        },
        'y': {
            'y1': [10, 20, 25, 30],
            'y2': [5, 15, 35, 50]
        }
    }

    # Отримання вибраних категорій від користувача
    selected_x = request.GET.get("x_category", "x1")  # За замовчуванням x1
    selected_y = request.GET.get("y_category", "y1")  # За замовчуванням y1

    # Створення DataFrame на основі вибору
    df = pd.DataFrame({
        'x': data_options['x'][selected_x],
        'y': data_options['y'][selected_y]
    })

    # Побудова графіка
    fig = px.line(df, x='x', y='y', title='Динамічний графік', markers=True)
    fig.update_layout(
        xaxis_title='Вісь X',
        yaxis_title='Вісь Y'
    )

    # Конвертація графіка у HTML
    plot_html = fig.to_html(full_html=False)

    context = {
        'plot_html': plot_html,
        'data_options': data_options,
        'selected_x': selected_x,
        'selected_y': selected_y
    }
    return render(request, "visual/visual.html", context)

