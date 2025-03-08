from django.contrib import admin

from .models import Budget, FinOperation, Category,GoalBudget,TransferBudget,TransferGoalBudget, Currency, PeriodicStreakTracker

# Register your models here.
admin.site.register(Budget)
admin.site.register(FinOperation)
admin.site.register(Category)
admin.site.register(GoalBudget)
admin.site.register(TransferBudget)
admin.site.register(TransferGoalBudget)
admin.site.register(Currency)
admin.site.register(PeriodicStreakTracker)