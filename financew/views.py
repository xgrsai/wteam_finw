from django.shortcuts import render, redirect

from .models import Budget, FinOperation
from .forms import BudgetForm, FinOperationForm

# Create your views here.
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

