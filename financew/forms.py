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
        fields = ['amount', 'type', 'time_interval', 'category']
        labels = {
            'amount': 'Сума',
            'type': 'Тип операції',
            'time_interval': 'Часовий інтервал',
            'category': 'Категорія операціії',
        #     'start_date': 'Дата початку операції'
        # }
        # widgets = {
        #     'start_date': forms.DateTimeInput(attrs={'time_type': 'datetime-local'}),
        # 
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Назва категорії'}
    
    # def clean_name(self):
    #     name = self.cleaned_data['name']
    #     if Category.objects.filter(name=name).exists():
    #         raise forms.ValidationError("Категорія з таким ім'ям вже існує.")
    #     return name
    
class GoalBudgetForm(forms.ModelForm):
    class Meta:
        model = GoalBudget
        fields = ['name', 'currency', 'target_amount', 'amount']
        labels = {'name':'Ім\'я для бюджету-цілі', 'currency': 'Валюта', 'target_amount': 'Ціль' , 'amount': 'Поточна сума'}

class TransferFromBudgetForm(forms.ModelForm):
    class Meta:
        model = TransferBudget
        fields = [ 'to_budget', 'amount']
        labels = { 'to_budget':'В який бюджет', 'amount':'Сума',
        }

class TransferFromGoalBudgetForm(forms.ModelForm):
    class Meta:
        model = TransferGoalBudget
        fields = [ 'to_goalbudget', 'amount']
        labels = { 'to_goalbudget':'В який бюджет-ціль', 'amount':'Сума',
        }

class TransferBudgetForm(forms.ModelForm):
    """Форма для трансферу з включеним """
    class Meta:
        model = TransferBudget
        fields = ['from_budget', 'to_budget', 'amount']
        labels = {'from_budget':'З якого бюджету', 'to_budget':'В який бюджет', 'amount':'Сума',
        }

class CurrencyForm(forms.Form):
    currency = forms.ChoiceField(
        choices=[(key, value) for key, value in CURRENCIES.items()],
        label="Вибір валюти",
        #initial= # бере першим зі словника
        widget=forms.Select(attrs={'onchange': 'this.form.submit()'}),

    )


# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')
#
#     def save(self, commit=True):
#         user = super(CustomUserCreationForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']
#         if commit:
#             user.save()
#         return user
#
# class CustomAuthenticationForm(AuthenticationForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password')
