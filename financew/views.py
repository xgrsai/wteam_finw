from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required
from django.http import Http404
from itertools import chain
from django.db import transaction
from copy import deepcopy
from django.http import JsonResponse
from .forecast import forecast_expenses
from django.db.models import Max
# from django.utils import timezone

from .constants import CURRENCIES
from .utils import get_exchange_rates, convert_to_currency, amount_in_currency, convert_currency_for_transfer
from .models import Budget, FinOperation, GoalBudget, Category, TransferBudget, TransferGoalBudget, Currency
from .forms import BudgetForm, FinOperationForm, GoalBudgetForm, CategoryForm,  TransferFromBudgetForm, TransferFromGoalBudgetForm, CurrencyForm

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
    goalbudgets = GoalBudget.objects.filter(owner=request.user).all() # всі бюджети-цілі користувача
    categories = Category.objects.filter(owner=request.user).all()#наявнi категорій користувача
    recent_operations = FinOperation.objects.filter(budget__owner=request.user).order_by('-date_added')[:10]# останні 10 фінансових операцій для поточного користувача
    # Отримуємо максимальну дату для кожної валюти
    latest_currencies = Currency.objects.exclude(currency="UAH").values('currency').annotate(latest_date=Max('date_added'))

    # Тепер отримуємо валюти за цією датою
    currencies = []
    for currency in latest_currencies:
        latest_currency = Currency.objects.filter(currency=currency['currency'], date_added=currency['latest_date']).first()
        if latest_currency:
            currencies.append(latest_currency)

    """форма для вибору яку валюту відобразити"""
    display_currency = request.GET.get('currency', request.session.get('display_currency', 'UAH'))# Отримуємо валюту з сесії (якщо є), або використовуємо дефолтну 'UAH'... Якщо параметр currency передано через GET-запит (наприклад, через URL: ?currency=USD), то він буде використаний. (щоб редірект не робити)
    currencydisplayform = CurrencyForm(initial={'currency': display_currency}) # Створюємо форму з ініціалізацією значення за замовчуванням
    selected_currency = request.GET.get('currency', None) # None якщо нічого не вибрано
    if selected_currency:
        request.session['display_currency'] = selected_currency # Якщо валюта вибрана, зберігаємо її в сесії
        # return redirect('financew:my') # чомусь погано працює тому через редірект
    
    """Обчислення загального балансу (і бюджетів) у вибраній валюті"""
    converted_budgets = []
    total_balance = 0
    for budget in budgets:
        converted_amount = amount_in_currency(display_currency, budget).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)# Конвертуємо баланс бюджету у вибрану валюту (+2 знаки після коми)
        
        converted_budgets.append({
            'budget': budget,
            'converted_amount': converted_amount,
        })

        total_balance += converted_amount
    
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
    context = {'budgets': converted_budgets, 'goalbudgets': goalbudgets, 'categories': categories, 'goalbudgetform':goalbudgetform, 'budgetform': budgetform, 'categoryform':categoryform, 'total_balance': total_balance, 'display_currency': display_currency, 'recent_operations':recent_operations, 'currencydisplayform':currencydisplayform, 'currencies':currencies}
    return render(request, 'financew/my.html', context) # потім дані з context можна використовувати у шаблоні 

@login_required
def transactions(request):
    """
    Відображає всі фінансові операції користувача з можливістю фільтрації.
    """
    operations = FinOperation.objects.filter(budget__owner=request.user).order_by('-date_added')
    budgets = Budget.objects.filter(owner=request.user)
    categories = Category.objects.all()  # Категорії можуть бути загальними

    # Отримуємо валюту відображення з GET-параметра або сесії
    rates = get_exchange_rates()
    # display_currency = request.GET.get('currency', request.session.get('display_currency', 'UAH'))
    # if display_currency not in ['UAH', 'USD', 'EUR']:
    #     display_currency = 'UAH'
    # request.session['display_currency'] = display_currency
    """форма для вибору яку валюту відобразити"""
    display_currency = request.GET.get('currency', request.session.get('display_currency', 'UAH'))# Отримуємо валюту з сесії (якщо є), або використовуємо дефолтну 'UAH'
    currencydisplayform = CurrencyForm(initial={'currency': display_currency}) # Створюємо форму з ініціалізацією значення за замовчуванням
    selected_currency = request.GET.get('currency', None) # None якщо нічого не вибрано
    if selected_currency:
        request.session['display_currency'] = selected_currency # Якщо валюта вибрана, зберігаємо її в сесії
        # return redirect('financew:transactions')



    # Отримуємо параметри фільтрів
    date = request.GET.get('date')
    budget_id = request.GET.get('budget')
    category_id = request.GET.get('category')
    operation_type = request.GET.get('type')

    # Застосовуємо фільтри
    if date:
        operations = operations.filter(date_added__date=date)
    if budget_id and budget_id.isdigit():
        operations = operations.filter(budget_id=int(budget_id))
    if category_id and category_id.isdigit():
        operations = operations.filter(category_id=int(category_id))
    if operation_type in ['income', 'expense']:
        operations = operations.filter(type=operation_type)

    # Конвертуємо суми операцій у вибрану валюту
    operations_with_converted = []
    for operation in operations:
        balance_in_uah = operation.amount if operation.budget.currency == 'UAH' else (
            operation.amount * rates[operation.budget.currency])
        converted_amount = convert_to_currency(balance_in_uah, display_currency, rates)
        operations_with_converted.append({
            'operation': operation,
            'converted_amount': converted_amount
        })

    context = {
        'operations_with_converted': operations_with_converted,
        'display_currency': display_currency,
        'currencies': ['UAH', 'USD', 'EUR'],
        'budgets': budgets,
        'categories': categories,
        'currencydisplayform':currencydisplayform,
    }
    return render(request, 'financew/transactions.html', context)

@login_required
def budget(request, budget_id):
    """сторінка бюджету з фінопераціями"""
    budget = Budget.objects.get(id=budget_id) 

    if budget.owner != request.user: # для того щоб не переглядати чужі бюджети
        raise Http404
    
    #для виведення фін-операцій
    finoperations = budget.finoperation_set.order_by('-date_added') # мінус означає від найновіших до старіших
        
    # форми для зміни поточного бюджету та форма для трансферу коштів і тд
    if request.method != 'POST':
        # No data submitted; create a blank form.
        budgetform = BudgetForm(instance=budget,prefix='budget')
        transferbudgetform = TransferFromBudgetForm(prefix='transfer-budget',user = request.user)
        transfergoalbudgetform = TransferFromGoalBudgetForm(prefix='transfer-goalbudget',user = request.user)
        new_finoperation_form = FinOperationForm(user = request.user,prefix='new-finoperation')
        edit_finoperation_forms = [FinOperationForm(instance=finoperation, user = request.user,prefix=f"new-finoperation-{finoperation.id}") for finoperation in finoperations]
    else:
        budgetform = BudgetForm(instance=budget, data=request.POST,prefix='budget') # бере існуючий запис і дані який надіслав користуввач (типу змінив текст)
        if budgetform.is_valid():
            budgetform.save() # типу запис до бд
            return redirect('financew:budget', budget_id=budget.id)
        
        #форми для редагування фіноперацій 
        edit_finoperation_forms = [(deepcopy(finoperation),FinOperationForm(data=request.POST,user = request.user,instance=finoperation, prefix=f"new-finoperation-{finoperation.id}")) for finoperation in finoperations]# deepcopy для старих значень бо instance їх автоматом оновлює
        validation = [(finoperation,edit_finoperation_form) for finoperation,edit_finoperation_form in edit_finoperation_forms if edit_finoperation_form.is_valid()] 
        if validation:
            for finoperation,edit_finoperation_form in validation:
                with transaction.atomic():
                    finop_amount_old = finoperation.amount
                    finop_type_old = finoperation.type
                    
                    edit_finoperation = edit_finoperation_form.save(commit=False)
                    print(finop_amount_old)
                    # Оновлення бюджету після зміни операції
                    if edit_finoperation.type == "expense" and finop_type_old == "expense":
                        budget.amount += finop_amount_old - edit_finoperation.amount
                    elif edit_finoperation.type == "income" and finop_type_old == "income":
                        budget.amount += edit_finoperation.amount - finop_amount_old
                    elif edit_finoperation.type == "income" and finop_type_old == "expense":
                        budget.amount += edit_finoperation.amount + finop_amount_old
                    else: #якщо нова операція це витрати а стара операція це прибуток
                        budget.amount -= edit_finoperation.amount + finop_amount_old
        
                    edit_finoperation.save() 
                    budget.save()
                    # edit_finoperation_form.save() # ніби тут краще
            return redirect('financew:budget', budget_id=budget.id)
        
        #форма для трансферу з поточного бюджету до просто бюджету
        transferbudgetform = TransferFromBudgetForm(data=request.POST,user = request.user,prefix='transfer-budget')
        if transferbudgetform.is_valid():
            with transaction.atomic(): # всі зміни в базі даних будуть виконані або всі разом (якщо всі операції успішні), або жодна (якщо виникне помилка).  
                new_transferbudget = transferbudgetform.save(commit=False) # не зберігати одразу до бд
                new_transferbudget.from_budget = budget #додати бюджет з якого надсилається
                #логіка зняття коштів та їх додавання по бюджетах
                to_budget = new_transferbudget.to_budget # в який бюджет заливаєм кошти
                if budget.currency == to_budget.currency:
                    to_budget.amount += new_transferbudget.amount 
                    budget.amount = budget.amount - new_transferbudget.amount 
                else:
                    to_budget.amount += convert_currency_for_transfer(budget.currency,to_budget.currency,new_transferbudget.amount) 
                    budget.amount = budget.amount - new_transferbudget.amount
                # зберегти в БД
                budget.save()
                to_budget.save()  
                new_transferbudget.save()  
            return redirect('financew:budget', budget_id=budget.id)

        #форма для трансферу з поточного бюджету до бюджету-цілі
        transfergoalbudgetform = TransferFromGoalBudgetForm(data=request.POST,user = request.user,prefix='transfer-goalbudget')
        if transfergoalbudgetform.is_valid():
            with transaction.atomic(): # всі зміни в базі даних будуть виконані або всі разом (якщо всі операції успішні), або жодна (якщо виникне помилка).  
                new_transfergoalbudget = transfergoalbudgetform.save(commit=False) # не зберігати одразу до бд
                new_transfergoalbudget.from_budget = budget #додати бюджет з якого надсилається
                #логіка зняття коштів та їх додавання по бюджетах
                to_budget = new_transfergoalbudget.to_goalbudget # в який бюджет заливаєм кошти
                if budget.currency == to_budget.currency:
                    to_budget.amount += new_transfergoalbudget.amount 
                    budget.amount = budget.amount - new_transfergoalbudget.amount 
                else:
                    to_budget.amount += convert_currency_for_transfer(budget.currency,to_budget.currency,new_transfergoalbudget.amount) 
                    budget.amount = budget.amount - new_transfergoalbudget.amount
                # зберегти в БД
                budget.save() # збереження бюджету з якого відправлвяли
                to_budget.save()  # це збереження бюджету-цілі
                new_transfergoalbudget.save() #це збереження запису
            return redirect('financew:budget', budget_id=budget.id)
        
        # форма для нової фіноперації 
        new_finoperation_form = FinOperationForm(data=request.POST, user = request.user, prefix='new-finoperation')
        if new_finoperation_form.is_valid():
            with transaction.atomic():
                new_finoperation = new_finoperation_form.save(commit=False) # commit=false не записує об'єкт в базу даних
                new_finoperation.budget = budget # зберегти запис за бюджетом який ми витягли з БД (на початку функції)
                if new_finoperation.type == "expense":
                    budget.amount = budget.amount - new_finoperation.amount
                elif new_finoperation.type == "income":
                    budget.amount = budget.amount + new_finoperation.amount
                budget.save()
                new_finoperation.save() # тут воно вже зберігає з правильним бюджетом
            return redirect('financew:budget', budget_id=budget_id)

    #для показу переведень бюджетів
    transfers_out = budget.budget_out_set.all() # Отримати всі перекази між бюджетами, де цей бюджет є відправником
    transfers_in = budget.budget_in_set.all() # Отримати всі перекази між бюджетами, де цей бюджет є отримувачем
    goal_transfers = TransferGoalBudget.objects.filter(from_budget=budget) # Отримати всі перекази, де цей бюджет надсилає гроші у цільовий бюджет (вирази насправді одинакові просто різні представлення (мається на увазі transfers_in = budget.budget_in_set.all()), тобто можна би було вказати TransferBudget.objects.filter(from_budget=budget))
    all_transfers = chain(transfers_out, transfers_in, goal_transfers)# Об'єднуємо всі перекази 
    transfers = sorted(all_transfers, key=lambda x: x.date_added, reverse=True)# Відсортувати за датою (воно автоматом в ліст перетворює) елементи в transfers досі є об'єктами класу
    context = {'budget': budget, 'finoperations': finoperations, 'transfers': transfers,'form': budgetform,'transferbudgetform': transferbudgetform, 'transfergoalbudgetform':transfergoalbudgetform, 'new_finoperation_form': new_finoperation_form,'edit_finoperation_forms':edit_finoperation_forms, 'finoperations_and_edit_forms': zip(finoperations,edit_finoperation_forms)}
    return render(request, 'financew/budget.html', context)


# @login_required
# def new_finoperation(request, budget_id):
#     """додати нову фіноперацію для бюджету"""
#     budget = Budget.objects.get(id=budget_id)

#     if budget.owner != request.user:
#         raise Http404

#     if request.method != 'POST':
#         # No data submitted; create a blank form.
#         form = FinOperationForm()
#     else:
#         # POST data submitted; process data.
#         form = FinOperationForm(data=request.POST)
#         if form.is_valid():
#             with transaction.atomic():
#                 new_finoperation = form.save(commit=False) # commit=false не записує об'єкт в базу даних
#                 new_finoperation.budget = budget # зберегти запис за бюджетом який ми витягли з БД (на початку функції)
#                 if new_finoperation.type == "expense":
#                     budget.amount = budget.amount - new_finoperation.amount
#                 elif new_finoperation.type == "income":
#                     budget.amount = budget.amount + new_finoperation.amount
#                 budget.save()
#                 new_finoperation.save() # тут воно вже зберігає з правильним бюджетом
#             return redirect('financew:budget', budget_id=budget_id)
        
#     # Display a blank or invalid form.
#     context = {'budget': budget, 'form': form}
#     return render(request, 'financew/new_finoperation.html', context) # потім дані з context можна використовувати у шаблоні 

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
def delete_budget(request, budget_id):
    """
    Видаляє бюджет за його ID. Доступно лише власнику бюджету.
    """
    budget = get_object_or_404(Budget, id=budget_id, owner=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('financew:my')

@login_required
def delete_goalbudget(request, goalbudget_id):
    """
    Видаляє бюджет-ціль за її ID. Доступно лише власнику бюджету-цілі.
    """
    goalbudget = get_object_or_404(GoalBudget, id=goalbudget_id, owner=request.user)
    if request.method == 'POST':
        goalbudget.delete()
        return redirect('financew:my')


@login_required
def delete_category(request, category_id):
    """
    Видаляє категорію за її ID. Доступно лише власнику категорії.
    """
    category = get_object_or_404(Category, id=category_id, owner=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('financew:my')


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
        finoperation.category = request.POST.get('category')
        # form = FinOperationForm(data=request.POST)

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
  
@login_required
def expenses_forecast(request, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id, owner=request.user)  # Змінив user -> owner
    except Budget.DoesNotExist:
        return JsonResponse({"error": "Бюджет не знайдено або немає доступу"}, status=404)

    predicted_expenses = forecast_expenses(budget)

    if predicted_expenses is None:
        return JsonResponse({"error": "Недостатньо даних для прогнозу"}, status=400)

    return JsonResponse({"predicted_expenses": predicted_expenses})




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

