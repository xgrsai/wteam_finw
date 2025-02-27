from django.utils import timezone
from .models import FinOperation, Budget


def check_and_execute_operations():
    """
    Автоматично перевіряє і виконує фінансові операції залежно від інтервалів.
    Враховує валюти, категорії та обробляє помилки.
    """
    now = timezone.now()
    operations = FinOperation.objects.filter(is_active=True)

    for operation in operations:
        try:
            if operation.should_execute():
                # Отримуємо пов'язаний бюджет
                budget = operation.budget

                # Перевіряємо, чи валюта операції співпадає з валютою бюджету
                if not operation.validate_currency_match(budget.currency):
                    print(f"Несумісність валюти для операції {operation} у бюджеті {budget}")
                    continue

                # Перевіряємо, чи є достатньо коштів для списання
                if budget.amount >= operation.amount:
                    # Списуємо кошти з бюджету
                    if operation.type == 'expense':
                        budget.amount -= operation.amount
                    elif operation.type == 'income':
                        budget.amount += operation.amount

                    budget.save()

                    # Оновлюємо дату останнього виконання операції
                    operation.last_execution = now
                    operation.save()
                    print(f"Успішно виконано операцію {operation} у бюджеті {budget}")
                else:
                    # Якщо коштів недостатньо, деактивуємо операцію та логуємо
                    operation.is_active = False
                    operation.save()
                    print(f"Недостатньо коштів для операції {operation} у бюджеті {budget}")
        except Exception as e:
            print(f"Помилка при виконанні операції {operation}: {str(e)}")