from django.contrib import admin

from .models import Budget, FinOperation, Category

# Register your models here.
admin.site.register(Budget)
admin.site.register(FinOperation)
admin.site.register(Category)
