from django import forms

from financew.constants import CURRENCIES, TIME_INTERVALS, FINOPERATION_TYPE
from financew.models import Budget 

class FinOperationTypeForm(forms.Form):
    """форма для вибору фільтрів для piechart"""
    finoperation_type = forms.ChoiceField(
        choices=[(key, value) for key, value in FINOPERATION_TYPE.items()],
        label="Вибір типу фіноперації",
        #initial= # бере першим зі словника
        # widget=forms.Select(attrs={'onchange': 'this.form.submit()'}),

    )
 
class WhichBudgetForm(forms.Form):
    """з якого бюдету взяти дані"""
    # Отримуємо список бюджетів, що належать поточному користувачу
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Отримуємо користувача з в'юшки
        super().__init__(*args, **kwargs)
        
        # Створюємо список варіантів для вибору, додавши "ВСІ"
        budgets = Budget.objects.filter(owner=user)
        budget_dict = {"all": "Всі"}  # Початковий елемент для "ВСІ"
        budget_dict.update({budget.id: budget.name for budget in budgets})
        
        # Перетворюємо словник в список кортежів для ChoiceField
        self.fields['budget_type'] = forms.ChoiceField(
            choices=[(key, value) for key, value in budget_dict.items()],
            label="Вибір бюджету",
            # widget=forms.Select(attrs={'onchange': 'this.form.submit()'})
        )
    
    