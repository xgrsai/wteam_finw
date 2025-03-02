from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.db.utils import IntegrityError
from itertools import chain

from .models import Budget, FinOperation, GoalBudget, Category, TransferBudget, TransferGoalBudget
from .forms import BudgetForm, FinOperationForm, GoalBudgetForm, CategoryForm

def index(request):
    """головна сторінка фінансиW з бюджетами"""
    # budgets = Budget.objects.all()
    # context = {'budgets': budgets}

    return render(request, "financew/index.html")

@login_required
def my(request):
    """головна сторінка фінансиW з бюджетом та додавання нового бюджету (те саме стосується і бюджетів-цілей)"""
    budgets = Budget.objects.filter(owner=request.user).all() # взяти всі бюджети що належать цьому користувачу
    goalbudgets = GoalBudget.objects.filter(owner=request.user).all()

    #наявнi категорій користувача
    categories = Category.objects.filter(owner=request.user).all()

    # форма для додавання нового бюджету та бюджету цілі
    if request.method != 'POST':
        # No data submitted; create a blank form.
        budgetform = BudgetForm(prefix='budget')
        goalbudgetform = GoalBudgetForm(prefix='goalbudget')
        categoryform = CategoryForm(prefix='categorybudget')

    else:
        #для форми бюджетів
        budgetform = BudgetForm(data=request.POST,prefix='budget' ) # аргумент передає значення полів форми
        if budgetform.is_valid():
            new_budget = budgetform.save(commit=False) # не зберігати одразу до бд
            new_budget.owner = request.user #додати власником поточного залогіненого користувача
            new_budget.save() # зберегти в бд
                
        #для форми бюджету-цілі
        goalbudgetform = GoalBudgetForm(data=request.POST,prefix='goalbudget') # аргумент передає значення полів форми
        if goalbudgetform.is_valid():
            new_goalbudget = goalbudgetform.save(commit=False) # не зберігати одразу до бд
            new_goalbudget.owner = request.user #додати власником поточного залогіненого користувача
            new_goalbudget.save() # зберегти в бд
        
        #для форми категорії
        categoryform = CategoryForm(data=request.POST,prefix='categorybudget') # аргумент передає значення полів форми
        if categoryform.is_valid():
            new_category = categoryform.save(commit=False) # не зберігати одразу до бд
            new_category.owner = request.user #додати власником поточного залогіненого користувача
            # try:    
            new_category.save()  # зберегти в БД
            #     messages.success(request, "Категорія успішно створена!")
            # except IntegrityError:
            #     messages.error(request, "Категорія з таким ім'ям вже існує.")

        return redirect('financew:my')
    
    # Display a blank or invalid form.
    context = {'budgets': budgets, 'goalbudgets': goalbudgets, 'categories': categories, 'goalbudgetform':goalbudgetform, 'budgetform': budgetform, 'categoryform':categoryform,}
                
               
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

    #для показу переведень бюджетів
    
    transfers_out = budget.budget_out_set.all() # Отримати всі перекази між бюджетами, де цей бюджет є відправником
    transfers_in = budget.budget_in_set.all() # Отримати всі перекази між бюджетами, де цей бюджет є отримувачем
    goal_transfers = TransferGoalBudget.objects.filter(from_budget=budget) # Отримати всі перекази, де цей бюджет надсилає гроші у цільовий бюджет

    # Об'єднуємо всі перекази
    all_transfers = chain(transfers_out, transfers_in, goal_transfers)
        
    # Відсортувати за датою
    transfers = sorted(all_transfers, key=lambda x: x.date_added, reverse=True)

    context = {'budget': budget, 'finoperations': finoperations, 'transfers': transfers,'form': form}
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

@login_required
def goalbudgets(request):
    goalbudgets = GoalBudget.objects.filter(owner=request.user).all() # взяти всі бюджети що належать цьому користувачу
        
    context = {'goalbudgets': goalbudgets}
    return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні  
  


# @login_required
# def add_category(request):
#     """Додає нову категорію для користувача"""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)  # Отримуємо JSON-дані
#             category_name = data.get("name").strip()  # Очищаємо пробіли

#             if not category_name:
#                 return JsonResponse({"message": "Назва категорії не може бути пустою"}, status=400)

#             # Перевіряємо, чи така категорія вже існує для цього користувача
#             category, created = Category.objects.get_or_create(
#                 name=category_name, owner=request.user
#             )

#             if created:
#                 return redirect('financew:my') #JsonResponse({"message": "Категорію додано успішно!"})
#             else:
#                 return JsonResponse({"message": "Така категорія вже існує!"}, status=400)
            
#         except Exception as e:
#             return JsonResponse({"message": f"Помилка: {str(e)}"}, status=500)

#     return JsonResponse({"message": "Дозволено тільки POST-запити"}, status=405)


# def new_goalbudget(request):
#     """додавання бюджету-цілі"""
#     if request.method != 'POST':
#         form = GoalBudgetForm()
#     else:
#         form = GoalBudgetForm(data=request.POST) # аргумент передає значення полів форми
#         if form.is_valid():
#             new_goalbudget = form.save(commit=False) # не зберігати одразу до бд
#             new_goalbudget.owner = request.user #додати власником поточного залогіненого користувача
#             new_goalbudget.save() # зберегти в бд
#             return redirect('financew:my')
    
    
#     context = {'goalbudget_form': form}    
#     return render(request,"financew/my.html",context)



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

