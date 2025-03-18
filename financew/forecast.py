import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from .models import FinOperation

def forecast_expenses(budget, days=30):
    transactions = FinOperation.objects.filter(budget=budget, type="expense").values("date_added", "amount")

    if not transactions.exists():
        return None  # Якщо немає витрат, повертаємо None

    df = pd.DataFrame(transactions)
    df.rename(columns={"date_added": "ds", "amount": "y"}, inplace=True)

    # Видаляємо часовий пояс
    df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)

    # Сортуємо за датою
    df = df.sort_values("ds")

    # Перетворюємо дати у числа (кількість днів від першої дати)
    df["days_since_start"] = (df["ds"] - df["ds"].min()).dt.days

    # Робимо всі витрати додатними
    df["y"] = df["y"].abs()

    # Навчаємо модель
    X = df["days_since_start"].values.reshape(-1, 1)
    y = df["y"].values

    model = LinearRegression()
    model.fit(X, y)

    # Прогнозуємо витрати на наступні `days` днів
    last_day = df["days_since_start"].max()
    future_days = np.array([last_day + i for i in range(1, days + 1)]).reshape(-1, 1)

    predicted_expenses = model.predict(future_days).sum()

    return round(predicted_expenses, 2)
