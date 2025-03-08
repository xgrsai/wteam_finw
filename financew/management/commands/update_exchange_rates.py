import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from financew.models import Currency

CURRENCIES_TO_FETCH = ['USD', 'EUR', 'UAH']

class Command(BaseCommand):
    help = "Оновлює курси валют у моделі Currency на основі даних НБУ"

    def handle(self, *args, **kwargs):
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            rates = {currency['cc']: Decimal(str(currency['rate'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                     for currency in data if currency['cc'] in CURRENCIES_TO_FETCH}
            
            rates['UAH'] = Decimal('1.00')  # Додаємо гривню як базову валюту

            # Оновлюємо або створюємо записи у таблиці Currency
            for currency, amount in rates.items():
                currency_obj, created = Currency.objects.update_or_create(
                    currency=currency,
                    date_added=timezone.now().date(),  # Унікальність запису за дату
                    defaults={"amount": amount}
                )
                action = "Створено" if created else "Оновлено"
                self.stdout.write(self.style.SUCCESS(f"{action}: {currency} - {amount}"))

        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Помилка отримання курсів валют: {e}"))

    