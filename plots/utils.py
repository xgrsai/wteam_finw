from financew.utils import get_exchange_rates 

def convert_df_amount(df, selected_currency):
    """для конвертації за валютою для датафреймів"""
    # print(df.info())
    rates = get_exchange_rates() 
    # rates = {currency: float(rate) for currency, rate in rates.items()} # переведення у float
    for currency in set(df['budget__currency']):
        print(currency,selected_currency)
        if selected_currency == currency:
            continue
        elif rates[selected_currency] < rates[currency]:   
            df.loc[df['budget__currency'] == currency, 'amount'] *= rates[currency]/rates[selected_currency]
            df['budget__currency'] = df['budget__currency'].replace(currency, selected_currency) # Заміна на 'обрану_валюту'
        elif rates[selected_currency] > rates[currency]:
            df.loc[df['budget__currency'] == currency, 'amount'] *= rates[currency]/rates[selected_currency]
            df['budget__currency'] = df['budget__currency'].replace(currency, selected_currency) # Заміна на 'обрану_валюту'
    return df            