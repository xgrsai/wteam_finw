import os
import django
import sys

# Налаштування середовища Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finw_project.settings')
django.setup()

# Імпорт функції з вашого додатку
from financew.cron import check_and_execute_operations

if __name__ == "__main__":
    try:
        check_and_execute_operations()
    except Exception as e:
        print(f"Помилка при виконанні задачі: {str(e)}", file=sys.stderr)
        sys.exit(1)