from django.urls import path, include
from accounts import views

app_name = "accounts"

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Include default auth urls.
    path('', include('django.contrib.auth.urls')), #Django автоматично додає всі URL-адреси, які потрібні для роботи системи аутентифікації (напр вхід вихід забув_пароль тощо)
    # Registration page.
    path('register/', views.register, name='register'),
]