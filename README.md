# wteam_finw
(UA)
Платформа управління особистими фінансами (FinW) – допомагає користувачам відстежувати витрати, прогнозувати бюджети та аналізувати фінансові звички.
<br>
(ENG)
Personal finance management platform (FinW) - helps users track expenses, forecast budgets, and analyze financial habits.

# Installation (UA)
## 1. Клонування репозиторію 
Перш за все, вам потрібно клонувати репозиторій проєкту на ваш локальний комп'ютер. Використовуйте команду git clone:<br>
`git clone <URL репозиторію>`
## 2. Створення віртуального середовища 
Для створення віртуального середовища використовуйте команду:<br>
`python -m venv <назва_середовища>`<br>
Активуйте віртуальне середовище:
- На Windows:
`.\venv\Scripts\activate`
- На macOS або Linux:
`source venv/bin/activate`
## 3. Встановлення залежностей
Для встановлення усіх необхідних бібліотек виконуємо команду:<br>
`pip install -r requirements.txt`
## 4. Міграція бази даних 
Після того, як ви створите віртуальне середовище та активуєте його, вам потрібно виконати міграцію бази даних. Це застосовує зміни, які були визначені в моделях вашого проєкту, до бази даних:<br>
`python manage.py migrate`<br>
Якщо є проблеми, то виконуємо команду:<br>
`python manage.py makemigrations`<br>
І потім:<br>
`python manage.py migrate`
## 5. Створення superuser
Для того щоб отримати доступ до адмін-панелі Django, потрібно створити суперкористувача. Це можна зробити за допомогою наступної команди:<br>
`python manage.py createsuperuser`
## 6.1 Виконайте команду перед першим `runserver`!!!
`python manage.py update_exchange_rates`
## 6.2. Запуск сервера Django 
Щоб запустити сервер Django і перевірити роботу вашого проєкту, скористайтеся командою:<br>
`python manage.py runserver`

# Installation (ENG)
## 1. Cloning the repository 
First of all, you need to clone the project repository to your local computer. Use the git clone command:<br>
`git clone <repository URL>`
## 2. Create a virtual environment 
To create a virtual environment, use the command: <br>
`python -m venv <environment_name>`<br><br>
Activate the virtual environment:
- On Windows:
`.\venv\Scripts\activate`
- On macOS or Linux:
`source venv/bin/activate`
## 3. Installing dependencies
To install all the necessary libraries, run the command:<br>
`pip install -r requirements.txt`.
## 4. Migrating the database 
After you create the virtual environment and activate it, you need to perform a database migration. This applies the changes that were defined in your project models to the database:<br>
`python manage.py migrate`<br>
If there are problems, then run the command:<br>
`python manage.py makemigrations`<br>
And then:<br>
`python manage.py migrate`
## 5. Creating a superuser
In order to access the Django admin panel, you need to create a superuser. This can be done with the following command:<br>
`python manage.py createsuperuser`
## 6.1. Execute the command before very first `runserver`!!!
`python manage.py update_exchange_rates`
## 6.2. Starting the Django server 
To start the Django server and check the operation of your project, use the command:<br>
`python manage.py runserver`

### Перегляньте відео:
[video.mp4](./video/video.mp4)