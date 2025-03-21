from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm



def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.
        form = UserCreationForm()
    else:
        # Process completed form.
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Log the user in and then redirect to home page.
            login(request, new_user)
            return redirect('financew:index')
    
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'registration/register.html', context)



















# # Тест на працездатність модуля accounts
# from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Accounts module працює!")

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('financew:my')  # Перенаправлення на головну сторінку після реєстрації
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('financew:my')  # Перенаправлення на головну сторінку після входу
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})

# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect('login')  # Перенаправлення на сторінку входу після виходу