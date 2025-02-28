from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .utils import get_exchange_rates, convert_to_currency
from decimal import Decimal, ROUND_HALF_UP

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # зовнішній ключ на користувача (власника бюджет)

    class Meta:
        verbose_name_plural = 'budgets'
    
    def __str__(self):
        """Повернути нормальним текстом"""
        return f"{self.name} {self.amount} {self.currency}"

    def total_balance_in_uah(self, request):
        """
        Обчислює загальний баланс у гривнях, конвертуючи USD і EUR за актуальним курсом.
        """
        if self.currency == "UAH":
            return self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        rates = get_exchange_rates(request)
        if self.currency in rates:
            converted_amount = (self.amount * rates[self.currency]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return converted_amount
        else:
            raise ValueError(f"Курс для валюти {self.currency} не знайдено")

    def total_balance_in_currency(self, target_currency, request):
        """
        Обчислює баланс у заданій валюті (UAH, USD, EUR).
        """
        amount_in_uah = self.total_balance_in_uah(request)
        rates = get_exchange_rates(request)
        return convert_to_currency(amount_in_uah, target_currency, rates)


class Category(models.Model):
    """категорії для фін операцій (напр. їжа, магазин, розваги (користувач сам їх дає))"""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE) # зовнішній ключ на користувача (власника категорії)

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

    start_date = models.DateTimeField(default=timezone.now) # Дата початку операції
    last_execution = models.DateTimeField(null=True, blank=True) # Дата останнього списання
    is_active = models.BooleanField(default=True) # Чи активна операція, по дефолту - активна

    class Meta:
        verbose_name_plural = 'finoperations'
    
    def __str__(self):
        """Повертаємо величину та тип операції"""
        return f"{self.category} {self.type} {self.amount} {self.time_interval}"

    def should_execute(self):
        if not self.is_active or self.time_interval == "one_time":
            return False

        now = timezone.now()
        if self.last_execution is None:
            return now >= self.start_date

        days_diff = (now - self.last_execution).days

        if self.time_interval == 'weekly':
            return days_diff >= 7
        elif self.time_interval == 'monthly':
            # Використовуємо relativedelta для точного визначення місяців
            months_diff = relativedelta(now, self.last_execution).months + (
                        relativedelta(now, self.last_execution).years * 12)
            return months_diff >= 1
        elif self.time_interval == 'annually':
            years_diff = relativedelta(now, self.last_execution).years
            return years_diff >= 1

        return False

    def validate_currency_match(self, budget_currency):
        """
        Перевіряємо, чи валюта операції співпадає з валютою бюджету.
        Валюта операції береться з бюджету.
        """
        return self.budget.currency == budget_currency

