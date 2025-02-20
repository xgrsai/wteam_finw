# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User
# from .models import Budget, FinOperation, Category
#
# class BudgetForm(forms.ModelForm):
#     class Meta:
#         model = Budget
#         fields = ['name','amount','currency']
#         labels = {'name':'Ім\'я','amount': '', 'currency': 'Валюта' }
#
# class FinOperationForm(forms.ModelForm):
#     class Meta:
#         model = FinOperation
#         fields = ['amount', 'type', 'time_interval', 'category']
#         labels = {'amount': 'Сума', 'type': 'Тип операції','time_interval': 'Часовий інтервал', 'category': 'Категорія операціії'}
#
# class CategoryForm(forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = ['name']
#         labels = {'name': 'Назва категорії'}
#
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
