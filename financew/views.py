from django.shortcuts import render

# Create your views here.
def index(request):
    """головна сторінка фінансиW"""
    return render(request, "financew/index.html")


#частина з візуалізацією 
import matplotlib.pyplot as plt
import io
import urllib, base64

def visualisation(request):
    """Сторінка візуалізації"""

    # Створення графіку
    plt.plot([1, 2, 3, 4], [10, 20, 25, 30], marker='o')
    plt.title('Приклад графіку')
    plt.xlabel('Вісь X')
    plt.ylabel('Вісь Y')

    # Збереження графіку в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    # Кодування графіку в base64 для передачі у шаблон
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Передача графіку у шаблон
    context = {
        'plot_image': image_base64
    }
    return render(request, "visual/visual.html", context)
