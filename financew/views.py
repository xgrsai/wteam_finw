from django.shortcuts import render, redirect
from .models import Budget, FinOperation
from .forms import BudgetForm, FinOperationForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
#from .forms import CustomUserCreationForm, CustomAuthenticationForm

from django.shortcuts import render, get_object_or_404, redirect

from decimal import Decimal



def index(request):

    """головна сторінка фінансиW з бюджетами"""
    budgets = Budget.objects.all()
    context = {'budgets': budgets}

    return render(request, "financew/index.html", context)

def budget(request, budget_id):
    """сторінка з бюджетами"""
    budget = Budget.objects.get(id=budget_id)

    finoperations = budget.finoperation_set.order_by('-date_added') # мінус означає від найновіших до старіших
    context = {'budget': budget, 'finoperations': finoperations}
    return render(request, 'financew/budget.html', context)

def new_finoperation(request, budget_id):
    """додати нову фіноперацію для бюджету"""
    budget = Budget.objects.get(id=budget_id)

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = FinOperationForm()
    else:
        # POST data submitted; process data.
        form = FinOperationForm(data=request.POST)
        if form.is_valid():
            new_finoperation = form.save(commit=False) # commit=false не записує об'єкт в базу даних
            new_finoperation.budget = budget # зберегти запис за бюджетом який ми витягли з БД (на початку функції)
            if new_finoperation.type == "expense":
                budget.amount = budget.amount - new_finoperation.amount
            elif new_finoperation.type == "income":
                budget.amount = budget.amount + new_finoperation.amount
            budget.save()
            new_finoperation.save() # тут воно вже зберігає з правильним бюджетом
            return redirect('financew:budget', budget_id=budget_id)
        
    # Display a blank or invalid form.
    context = {'budget': budget, 'form': form}
    return render(request, 'financew/new_finoperation.html', context) # потім дані з context можна використовувати у шаблоні 


# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('/index')  # Перенаправлення на головну сторінку після реєстрації
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})
#
# def user_login(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('/index')  # Перенаправлення на головну сторінку після входу
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})
#
# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect('login')  # Перенаправлення на сторінку входу після виходу

def delete_finoperation(request, finoperation_id):
    """Видалення фінансової операції та оновлення бюджету"""
    finoperation = FinOperation.objects.get(id=finoperation_id)
    budget = finoperation.budget

    # Оновлення бюджету при видаленні операції
    if finoperation.type == "expense":
        budget.amount += finoperation.amount
    elif finoperation.type == "income":
        budget.amount -= finoperation.amount
    budget.save()

    finoperation.delete()
    return redirect('financew:budget', budget_id=budget.id)

def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id)
    
    if request.method == 'POST':
        # Редагувати дані бюджету
        budget.name = request.POST.get('name')
        budget.amount = float(request.POST.get('amount'))
        budget.currency = request.POST.get('currency')
        budget.save()
        return redirect('financew:budget', budget_id=budget.id)

    context = {'budget': budget}
    return render(request, 'financew/edit_budget.html', context)

# Редагування фінансової операції

def edit_finoperation(request, finoperation_id):
    finoperation = get_object_or_404(FinOperation, id=finoperation_id)
    budget = finoperation.budget

    if request.method == 'POST':
        # Перетворення суми на Decimal
        finoperation.amount = Decimal(request.POST.get('amount'))
        finoperation.type = request.POST.get('type')
        finoperation.save()

        # Оновлення бюджету після зміни операції
        if finoperation.type == "expense":
            budget.amount -= finoperation.amount
        elif finoperation.type == "income":
            budget.amount += finoperation.amount
        budget.save()

        return redirect('financew:budget', budget_id=budget.id)

    context = {'finoperation': finoperation, 'budget': budget}
    return render(request, 'financew/edit_finoperation.html', context)

