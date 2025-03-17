# wteam_finw
(UA)
Платформа управління особистими фінансами (FinW) – допомагає користувачам відстежувати витрати, прогнозувати бюджети та аналізувати фінансові звички.

(ENG)
Personal finance management platform (FinW) - helps users track expenses, forecast budgets, and analyze financial habits.

# Installation (UA)
## 1. Клонування репозиторію 
Перш за все, вам потрібно клонувати репозиторій проєкту на ваш локальний комп'ютер. Використовуйте команду git clone:
`git clone <URL репозиторію>`
## 2. Створення віртуального середовища 
`python -m venv <назва_середовища>`
Активуйте віртуальне середовище
### На Windows:
`.\venv\Scripts\activate`
### На macOS або Linux:
`source venv/bin/activate`
## 3. Міграція бази даних 
Після того, як ви створите віртуальне середовище та активуєте його, вам потрібно виконати міграцію бази даних. Це застосовує зміни, які були визначені в моделях вашого проєкту, до бази даних.
`python manage.py migrate`
## 4. Створення superuser
Для того щоб отримати доступ до адмін-панелі Django, потрібно створити суперкористувача. Це можна зробити за допомогою наступної команди:
`python manage.py createsuperuser`
## 5. Запуск сервера Django 
Щоб запустити сервер Django і перевірити роботу вашого проєкту, скористайтеся командою:
`python manage.py runserver`

# Installation (ENG)
## 1. Cloning the repository 
First of all, you need to clone the project repository to your local computer. Use the git clone command:
`git clone <repository URL>`
## 2. Create a virtual environment 
`python -m venv <environment_name>`
Activate the virtual environment
### On Windows:
`.\venv\Scripts\activate`
### On macOS or Linux:
`source venv/bin/activate`
## 3. Migrating the database 
After you create the virtual environment and activate it, you need to perform a database migration. This applies the changes that were defined in your project models to the database.
`python manage.py migrate`
## 4. Creating a superuser
In order to access the Django admin panel, you need to create a superuser. This can be done with the following command:
`python manage.py createsuperuser`
## 5. Starting the Django server 
To start the Django server and check the operation of your project, use the command:
`python manage.py runserver`