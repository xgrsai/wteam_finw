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
    amount = models.DecimalField(max_digits=19,decimal_places=2)
    
    class Meta:
        verbose_name_plural = 'budgets'
    
    def __str__(self):
        """Повернути нормальним текстом"""
        return f"{self.amount}"

class FinOperation(models.Model):
    """Фінансова операція яку здійснює користувач"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE) # бюджет може мати багато фін. операцій
    FinOperationType = models.TextChoices("FinOperationType", "INCOME EXPENSE") # прибуток та витрати
    operation_amount = models.DecimalField(max_digits=19,decimal_places=2)
    fin_operation_type = models.CharField(blank=False, choices=FinOperationType.choices, max_length=7)
    fin_operation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'finoperations'
    
    def __str__(self):
        """Повертаємо величину та тип операції"""
        return f"{self.fin_operation_type} {self.operation_amount}"
    


    

