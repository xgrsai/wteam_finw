from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from .models import Budget, FinOperation
from .forms import BudgetForm, FinOperationForm

def index(request):
    """головна сторінка фінансиW з бюджетами"""
    # budgets = Budget.objects.all()
    # context = {'budgets': budgets}

    return render(request, "financew/index.html")

@login_required
def my(request):
    """головна сторінка фінансиW з бюджетами та додати новий бюджет"""
    budgets = Budget.objects.filter(owner=request.user).all() # взяти всі бюджети що належать цьому користувачу

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BudgetForm()

    else:
        form = BudgetForm(data=request.POST) # аргумент передає значення полів форми
        if form.is_valid():
            new_budget = form.save(commit=False) # не зберігати одразу до бд
            new_budget.owner = request.user #додати власником поточного залогіненого користувача
            new_budget.save() # зберегти в бд
            return redirect('financew:my')
        
        # Display a blank or invalid form.
        
    context = {'budgets': budgets, 'form':form }
    return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні 

@login_required
def new_budget(request):
    """додати новий бюджет"""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BudgetForm()
    else:
        # POST data submitted; process data.
        form = BudgetForm(data=request.POST) # аргумент передає значення полів форми
        if form.is_valid():
            new_budget = form.save(commit=False) # не зберігати одразу до бд
            new_budget.owner = request.user #додати власником поточного залогіненого користувача
            new_budget.save() # зберегти в бд
            return redirect('financew:my')
    
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні 

@login_required
def budget(request, budget_id):
    """сторінка з бюджетами"""
    budget = Budget.objects.get(id=budget_id) 

    finoperations = budget.finoperation_set.order_by('-date_added') # мінус означає від найновіших до старіших
    context = {'budget': budget, 'finoperations': finoperations}
    return render(request, 'financew/budget.html', context)

@login_required
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

@login_required
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

@login_required
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

@login_required
def edit_finoperation(request, finoperation_id):
    """Редагування фінансової операції"""
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

