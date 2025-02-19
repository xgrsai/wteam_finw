from django.contrib import admin

from .models import Budget, FinOperation

# Register your models here.
admin.site.register(Budget)
admin.site.register(FinOperation)
