"""допоміжні функції (переважно для views.py)"""

import requests
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from datetime import timedelta


def get_exchange_rates(request):
    """
    Отримує актуальні курси валют від НБУ.
    Повертає словник із курсами для USD і EUR до UAH.
    """

    # Перевіряємо, чи є курси у сесії та чи вони актуальні
    session_rates = request.session.get('exchange_rates', {})
    rates_timestamp = request.session.get('rates_timestamp', None)

    # Якщо курси є і вони оновлені сьогодні, повертаємо їх
    if session_rates and rates_timestamp:
        last_updated = timezone.datetime.fromisoformat(rates_timestamp)
        if (timezone.now() - last_updated) < timedelta(days=1):
            rates = {k: Decimal(v) for k, v in session_rates.items()}
            rates['UAH'] = Decimal('1.00')
            return rates

    # Якщо курсів немає або вони застарілі, отримуємо нові
    try:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        data = response.json()

        rates = {}
        for currency in data:
            if currency['cc'] in ['USD', 'EUR']:
                rates[currency['cc']] = Decimal(str(currency['rate'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # Зберігаємо курси у сесії
        request.session['exchange_rates'] = {k: str(v) for k, v in rates.items()}
        request.session['rates_timestamp'] = timezone.now().isoformat()
    except requests.RequestException as e:
        print(f"Помилка при отриманні курсів валют: {e}")
        rates = {
            'USD': Decimal('41.1234').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'EUR': Decimal('45.6789').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        }
        request.session['exchange_rates'] = {k: str(v) for k, v in rates.items()}
        request.session['rates_timestamp'] = timezone.now().isoformat()

        # Додаємо UAH як базову валюту (1 UAH = 1 UAH)
    rates['UAH'] = Decimal('1.00')
    return rates


def convert_to_currency(amount_in_uah, target_currency, rates):
    """
    Конвертує суму з UAH у задану валюту (UAH, USD, EUR).
    """
    if target_currency not in rates:
        raise ValueError(f"Курс для валюти {target_currency} не знайдено")

    # Конвертуємо з UAH у target_currency
    converted_amount = (amount_in_uah / rates[target_currency]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return converted_amount