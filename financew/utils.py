"""допоміжні функції (переважно для views.py)"""
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone

from .models import Currency 

def get_exchange_rates():
    """Отримання актуальних курсів"""
    currencies = Currency.objects.filter(date_added=timezone.localdate())
    if not currencies:
        latest_date = Currency.objects.all().order_by('-date_added').values('date_added').first()
        currencies = Currency.objects.filter(date_added=latest_date['date_added'])
    rates = {}
    # print(len(currencies))
    for currency in currencies:
        rates[currency.currency] = Decimal(str(currency.amount)).quantize(Decimal('0.01'))
    return rates

def amount_in_currency(selected_currency, budget):
    """конвертація валюти (для бюджету) за актуальним курсом."""
    if selected_currency != budget.currency:
        #print(budget)
        rates = get_exchange_rates()
        if rates[selected_currency] < rates[budget.currency] and rates[selected_currency]==Decimal('1.0'): # перевіряє чи вибрана валюта = основній валюті (основна валюта це та що В БД = 1.0)
            amount = budget.amount * rates[budget.currency]
            return amount
        elif rates[budget.currency]!=Decimal('1.0') and rates[selected_currency] < rates[budget.currency]: #якщо вибрана валюта менша за валюту поточного бюджетну то для її розрахунку ділимо курс меншої на курс більшої
            amount = budget.amount * rates[selected_currency]/rates[budget.currency]
            return amount
        elif rates[budget.currency]!=Decimal('1.0') and rates[selected_currency] > rates[budget.currency]: #якщо вибрана загальна валюта більша за валюту поточного бюджетну то для її розрахунку ділимо курс меншої на курс більшої
            amount = budget.amount * rates[budget.currency]/rates[selected_currency]
            return amount
        elif rates[budget.currency]==Decimal('1.0'): # для бюджетів з основною валютою (не потрібно порівнювати оскільки це основна валюта)
            amount = budget.amount * rates[budget.currency]/rates[selected_currency]
            return amount
    else:
        return budget.amount

def convert_currency_for_transfer(from_currency, to_currency, amount_to_transfer):
    """конвертувати до певної валюти для трансферу"""
    rates = get_exchange_rates()
    amount = amount_to_transfer*rates[from_currency]/rates[to_currency]
    return amount
   

# def get_exchange_rates(request):
#     """
#     Отримує актуальні курси валют від НБУ.
#     Повертає словник із курсами для USD і EUR до UAH.
#     """

#     # Перевіряємо, чи є курси у сесії та чи вони актуальні
#     session_rates = request.session.get('exchange_rates', {})
#     rates_timestamp = request.session.get('rates_timestamp', None)

#     # Якщо курси є і вони оновлені сьогодні, повертаємо їх
#     if session_rates and rates_timestamp:
#         last_updated = timezone.datetime.fromisoformat(rates_timestamp)
#         if (timezone.now() - last_updated) < timedelta(days=1):
#             rates = {k: Decimal(v) for k, v in session_rates.items()}
#             rates['UAH'] = Decimal('1.00')
#             return rates

#     # Якщо курсів немає або вони застарілі, отримуємо нові
#     try:
#         url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
#         response = requests.get(url)
#         response.raise_for_status()  # Перевірка на помилки HTTP
#         data = response.json()

#         rates = {}
#         for currency in data:
#             if currency['cc'] in ['USD', 'EUR']:
#                 rates[currency['cc']] = Decimal(str(currency['rate'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         # Зберігаємо курси у сесії
#         request.session['exchange_rates'] = {k: str(v) for k, v in rates.items()}
#         request.session['rates_timestamp'] = timezone.now().isoformat()
#     except requests.RequestException as e:
#         print(f"Помилка при отриманні курсів валют: {e}")
#         rates = {
#             'USD': Decimal('41.1234').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
#             'EUR': Decimal('45.6789').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         }
#         request.session['exchange_rates'] = {k: str(v) for k, v in rates.items()}
#         request.session['rates_timestamp'] = timezone.now().isoformat()

#         # Додаємо UAH як базову валюту (1 UAH = 1 UAH)
#     rates['UAH'] = Decimal('1.00')
#     return rates

def convert_to_currency(amount_in_uah, target_currency, rates):
    """Конвертує суму з UAH у задану валюту (UAH, USD, EUR)."""
    if target_currency not in rates:
        raise ValueError(f"Курс для валюти {target_currency} не знайдено")

    # Конвертуємо з UAH у target_currency
    converted_amount = (amount_in_uah / rates[target_currency]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return converted_amount