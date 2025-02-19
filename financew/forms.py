from django import forms

from .models import Budget, FinOperation

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount']
        labels = {'amount': ''}

class FinOperationForm(forms.ModelForm):
    class Meta:
        model = FinOperation
        fields = ['amount', 'type']
        labels = {'amount': 'Сума', 'type': 'Тип операції'}
