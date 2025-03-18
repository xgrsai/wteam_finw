"""виконання фінансових операцій залежно від інтервалів"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from financew.models import FinOperation  
from financew.utils import get_exchange_rates 

class Command(BaseCommand):
    help = 'Перевіряє та виконує фінансові операції залежно від інтервалів'

    def handle(self, *args, **kwargs):
        """
        Автоматично перевіряє і виконує фінансові операції залежно від інтервалів.
        Враховує валюти, категорії та обробляє помилки.
        Конвертує суми з USD/EUR в UAH перед списанням.
        """
        now = timezone.now()
        operations = FinOperation.objects.filter(is_active=True)
        rates = get_exchange_rates()  # Отримуємо актуальні курси валют

        for operation in operations:
            try:
                if operation.should_execute():
                    # Отримуємо пов'язаний бюджет
                    budget = operation.budget

                    # Перевіряємо, чи валюта операції співпадає з валютою бюджету
                    if not operation.validate_currency_match(budget.currency):
                        self.stdout.write(f"Несумісність валюти для операції {operation} у бюджеті {budget}")
                        continue

                    # Конвертуємо суму операції в UAH, якщо бюджет у USD або EUR
                    amount_in_uah = operation.amount
                    if budget.currency != "UAH":
                        if budget.currency in rates:
                            amount_in_uah = operation.amount * rates[budget.currency]
                        else:
                            self.stdout.write(f"Курс для валюти {budget.currency} не знайдено")
                            continue

                    # Перевіряємо, чи є достатньо коштів для списання
                    if budget.amount >= amount_in_uah:
                        # Списуємо кошти з бюджету
                        if operation.type == 'expense':
                            budget.amount -= amount_in_uah
                        elif operation.type == 'income':
                            budget.amount += amount_in_uah

                        budget.save()

                        # Оновлюємо дату останнього виконання операції
                        operation.last_execution = now
                        operation.save()
                        self.stdout.write(f"Успішно виконано операцію {operation} у бюджеті {budget}")
                    else:
                        # Якщо коштів недостатньо, деактивуємо операцію та логуємо
                        operation.is_active = False
                        operation.save()
                        self.stdout.write(f"Недостатньо коштів для операції {operation} у бюджеті {budget}")
            except Exception as e:
                self.stdout.write(f"Помилка при виконанні операції {operation}: {str(e)}")
        self.stdout.write("Команда виконана успішно!")