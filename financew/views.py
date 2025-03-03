from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Budget, FinOperation
from .forms import BudgetForm, FinOperationForm
from .utils import get_exchange_rates, convert_to_currency

from django.utils import timezone

def index(request):
    """головна сторінка фінансиW з бюджетами"""
    # budgets = Budget.objects.all()
    # context = {'budgets': budgets}

    return render(request, "financew/index.html")

@login_required
def my(request):
    """
    Головна сторінка ФінансиW з бюджетом та загальним балансом у вибраній валюті.
    Відображає особистий кабінет користувача та дозволяє додавати нові бюджети.
    """
    budgets = Budget.objects.filter(owner=request.user).all() # взяти всі бюджети що належать цьому користувачу
    rates = get_exchange_rates(request)

    # Отримуємо останні 5 фінансових операцій для поточного користувача
    recent_operations = FinOperation.objects.filter(budget__owner=request.user).order_by('-date_added')[:5]

    # Отримуємо валюту відображення з GET-параметра або сесії
    display_currency = request.GET.get('currency', request.session.get('display_currency', 'UAH'))
    if display_currency not in ['UAH', 'USD', 'EUR']:
        display_currency = 'UAH'

    # Зберігаємо вибір валюти у сесії
    request.session['display_currency'] = display_currency

    # Обчислення загального балансу і конвертованих сум у вибраній валюті
    total_in_uah = Decimal('0')
    budgets_with_converted = []
    for budget in budgets:
        balance_in_uah = budget.total_balance_in_uah(request)
        print(
            f"Budget: {budget.name}, Currency: {budget.currency}, Amount: {budget.amount}, Balance in UAH: {balance_in_uah}")
        total_in_uah += balance_in_uah

        # Конвертуємо баланс бюджету у вибрану валюту
        converted_balance = convert_to_currency(balance_in_uah, display_currency, rates)
        budgets_with_converted.append({
            'budget': budget,
            'converted_balance': converted_balance
        })

    total_balance = convert_to_currency(total_in_uah, display_currency, rates)

    # форма для додавання нового бюджету
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
        
    context = {'budgets_with_converted': budgets_with_converted, 'budgets': budgets, 'total_balance': total_balance, 'display_currency': display_currency, 'form':form, 'currencies': ['UAH', 'USD', 'EUR'], 'recent_operations':recent_operations}
    return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні 

 

@login_required
def budget(request, budget_id):
    """сторінка бюджету з фінопераціями"""
    budget = Budget.objects.get(id=budget_id) 

    if budget.owner != request.user: # для того щоб не переглядати чужі бюджети
        raise Http404

    # форма для зміни поточного бюджету
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = BudgetForm(instance=budget)
    else:
        form = BudgetForm(instance=budget, data=request.POST) # бере існуючий запис і дані який надіслав користуввач (типу змінив текст)
        if form.is_valid():
            form.save() # типу запис до бд
            return redirect('financew:budget', budget_id=budget.id)


    finoperations = budget.finoperation_set.order_by('-date_added') # мінус означає від найновіших до старіших
    context = {'budget': budget, 'finoperations': finoperations, 'form': form}
    return render(request, 'financew/budget.html', context)


@login_required
def new_finoperation(request, budget_id):
    """додати нову фіноперацію для бюджету"""
    budget = Budget.objects.get(id=budget_id)

    if budget.owner != request.user:
        raise Http404

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

    if budget.owner != request.user:
        raise Http404

    # Оновлення бюджету при видаленні операції
    if finoperation.type == "expense":
        budget.amount += finoperation.amount
    elif finoperation.type == "income":
        budget.amount -= finoperation.amount
    budget.save()

    finoperation.delete()
    return redirect('financew:budget', budget_id=budget.id)


@login_required
def edit_finoperation(request, finoperation_id):
    """Редагування фінансової операції"""
    finoperation = get_object_or_404(FinOperation, id=finoperation_id)
    budget = finoperation.budget

    if budget.owner != request.user:
        raise Http404

    if request.method == 'POST':
        # Перетворення суми на Decimal
        finop_amount_old = finoperation.amount
        finop_type_old = finoperation.type
        finoperation.amount = Decimal(request.POST.get('amount'))
        finoperation.type = request.POST.get('type')

        # Оновлення бюджету після зміни операції
        if finoperation.type == "expense" and finop_type_old == "expense":
            budget.amount += finop_amount_old - finoperation.amount
        elif finoperation.type == "income" and finop_type_old == "income":
            budget.amount += finoperation.amount - finop_amount_old
        elif finoperation.type == "income" and finop_type_old == "expense":
            budget.amount += finoperation.amount + finop_amount_old
        else: #якщо нова операція це витрати а стара операція це прибуток
            budget.amount -= finoperation.amount + finop_amount_old
        
        finoperation.save() # ніби тут краще
        budget.save()

        return redirect('financew:budget', budget_id=budget.id)

    context = {'finoperation': finoperation, 'budget': budget}
    return render(request, 'financew/budget.html', context)

# @login_required
# def new_budget(request):
#     """додати новий бюджет"""
#     if request.method != 'POST':
#         # No data submitted; create a blank form.
#         form = BudgetForm()
#     else:
#         # POST data submitted; process data.
#         form = BudgetForm(data=request.POST) # аргумент передає значення полів форми
#         if form.is_valid():
#             new_budget = form.save(commit=False) # не зберігати одразу до бд
#             new_budget.owner = request.user #додати власником поточного залогіненого користувача
#             new_budget.save() # зберегти в бд
#             return redirect('financew:my')
    
#     # Display a blank or invalid form.
#     context = {'form': form}
#     return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні

# @login_required
# def edit_budget(request, budget_id):
#     """Edit an existing entry."""
#     budget = Budget.objects.get(id=budget_id) # отримання запису по id
    
#     if budget.owner != request.user:
#         raise Http404

#     if request.method != 'POST':
#         # Initial request; pre-fill form with the current entry.
#         form = BudgetForm(instance=budget) # означає, що форма буде заповнена даними з конкретного entry, який ми передали як instance
#     else:
#         # POST data submitted; process data.
#         form = BudgetForm(instance=budget, data=request.POST) # бере існуючий запис і дані який надіслав користуввач (типу змінив текст)
#         if form.is_valid():
#             form.save() # типу запис до бд
#             return redirect('financew:budget', budget_id=budget.id)
        
#     context = {'budget': budget, 'form': form}
#     return render(request, 'financew/budget.html', context)

# @login_required
# def edit_budget(request, budget_id):
#     budget = get_object_or_404(Budget, id=budget_id)
    
#     if budget.owner != request.user:
#         raise Http404

#     if request.method == 'POST':
#         # Редагувати дані бюджету
#         budget.name = request.POST.get('name')
#         budget.amount = float(request.POST.get('amount'))
#         budget.currency = request.POST.get('currency')
#         budget.save()
#         return redirect('financew:budget', budget_id=budget.id)

#     context = {'budget': budget}
#     return render(request, 'financew/budget.html', context)

