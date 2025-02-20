from django.db import models
"""1. Категорія (Category)
name — Назва категорії (наприклад, "Ресторан", "Магазин", "Заробітня плата", "Віддали борг") [користувач може сам створювати категорії]
user_id (FK) - якому користувачу належить категорія

2. Фінансова операція (Fin Opration)
user_id (FK) — Ідентифікатор користувача (зв'язок з User).
category_id (FK) — Ідентифікатор категорії (зв'язок з Category).
budget_id (FK) — одна операція може бути частиною конкретного бюджету
operation_amount — Сума операції.
transaction_type — Тип операції: 'income' або 'expense' (лише дві)
transaction_date — Дата та час транзакції.

3. Бюджет (Budget) - бюджет один
user_id (FK)
budget_amount — Загальна сума бюджету."""

# Create your models here.
class Budget(models.Model):
    """Бюджет яким володіє користувач"""
    CURRENCIES = {
        "UAH": "UAH",
        "USD": "USD",
        "EUR": "EUR",
    }

    amount = models.DecimalField(max_digits=19,decimal_places=2)
    name = models.CharField(max_length=200, null=True) # імя гаманця
    currency = models.CharField(blank=False, choices=CURRENCIES, default="UAH", max_length=17)

    class Meta:
        verbose_name_plural = 'budgets'
    
    def __str__(self):
        """Повернути нормальним текстом"""
        return f"{self.name} {self.amount}"

class Category(models.Model):
    """категорії для фін операцій (напр. їжа, магазин, розваги (користувач сам їх дає))"""
    name = models.CharField(max_length=200)
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        """Повернути нормальним текстом"""
        return f"{self.name}"

class FinOperation(models.Model):
    """Фінансова операція яку здійснює користувач"""
    TIME_INTERVALS = {
        "one_time": "Одноразовий",
        "weekly": "Щотижня",
        "monthly": "Щомісяця",
        "annually": "Щорічно",
    }
    FINOPERATION_TYPE = {
        "income": "Прибуток",
        "expense": "Витрати",
    }
    #FinOperationType = models.TextChoices("FinOperationType", "INCOME EXPENSE") 
    
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE) # бюджет може мати багато фін. операцій
    amount = models.DecimalField(max_digits=19,decimal_places=2)
    type = models.CharField(blank=False, choices=FINOPERATION_TYPE, max_length=7)# прибуток та витрати
    date_added = models.DateTimeField(auto_now_add=True)
    time_interval = models.CharField(blank=False, choices=TIME_INTERVALS, default="one_time", max_length=17)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'finoperations'
    
    def __str__(self):
        """Повертаємо величину та тип операції"""
        return f"{self.category} {self.type} {self.amount} {self.time_interval}"
    



    

