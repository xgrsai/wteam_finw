from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Budget, FinOperation, Category, GoalBudget, TransferBudget, TransferGoalBudget
from .constants import CURRENCIES

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name','amount','currency']
        labels = {'name':'Ім\'я','amount': 'Сума', 'currency': 'Валюта' }

class FinOperationForm(forms.ModelForm):
    
    class Meta:
        model = FinOperation
        fields = ['type', 'amount',  'time_interval', 'category','is_active']
        labels = {
            'amount': 'Сума',
            'type': 'Тип операції',
            'time_interval': 'Часовий інтервал',
            'category': 'Категорія операціії',
            'is_active': 'Чи активна',
        #     'start_date': 'Дата початку операції'
        # } 
        
        # widgets = {
        
        #     'start_date': forms.DateTimeInput(attrs={'time_type': 'datetime-local'}),

        # 
        }

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'time_interval': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    


    def __init__(self, *args, **kwargs):
        """щоб виводило категорії які належеть лише користувачу"""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Якщо користувач переданий, фільтруємо категорії
        if user:
            self.fields['category'].queryset = Category.objects.filter(owner=user)    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Назва категорії'}
    
class GoalBudgetForm(forms.ModelForm):
    """форма для створення бюджету-цілі"""
    class Meta:
        model = GoalBudget
        fields = ['name', 'currency', 'target_amount', 'amount']
        labels = {'name':'Ім\'я для бюджету-цілі', 'currency': 'Валюта', 'target_amount': 'Ціль' , 'amount': 'Поточна сума'}   

class TransferFromBudgetForm(forms.ModelForm):
    """трансфер зі сторінки бюджету в бюджет"""
    class Meta:
        model = TransferBudget
        fields = [ 'to_budget', 'amount']
        labels = { 'to_budget':'В який бюджет', 'amount':'Сума',
        }
    def __init__(self, *args, **kwargs):
        """щоб виводило [name] які належеть лише користувачу"""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Якщо користувач переданий, фільтруємо категорії
        if user:
            self.fields['to_budget'].queryset = Budget.objects.filter(owner=user)     

class TransferFromGoalBudgetForm(forms.ModelForm):
    """трансфер зі сторінки бюджету в бюджет-ціль"""
    class Meta:
        model = TransferGoalBudget
        fields = [ 'to_goalbudget', 'amount']
        labels = { 'to_goalbudget':'В який бюджет-ціль', 'amount':'Сума',
        }
    def __init__(self, *args, **kwargs):
        """щоб виводило [name] які належеть лише користувачу"""
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Якщо користувач переданий, фільтруємо категорії
        if user:
            self.fields['to_goalbudget'].queryset = GoalBudget.objects.filter(owner=user) 

class TransferBudgetForm(forms.ModelForm):
    """Форма для трансферу з бюджету в бюджет"""
    class Meta:
        model = TransferBudget
        fields = ['from_budget', 'to_budget', 'amount']
        labels = {'from_budget':'З якого бюджету', 'to_budget':'В який бюджет', 'amount':'Сума',
        }

class CurrencyForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[(key, value) for key, value in CURRENCIES.items()],
        label="Вибір валюти відображення",
        #initial= # бере першим зі словника
        widget=forms.Select(attrs={'onchange': 'this.form.submit()',"class": "form-control"}),

    )
