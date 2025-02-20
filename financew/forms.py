from django import forms

from .models import Budget, FinOperation, Category

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name','amount','currency']
        labels = {'name':'Ім\'я','amount': '', 'currency': 'Валюта' }

class FinOperationForm(forms.ModelForm):
    class Meta:
        model = FinOperation
        fields = ['amount', 'type', 'time_interval', 'category']
        labels = {'amount': 'Сума', 'type': 'Тип операції','time_interval': 'Часовий інтервал', 'category': 'Категорія операціії'}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Назва категорії'}        
