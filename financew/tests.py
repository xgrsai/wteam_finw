from django.test import TestCase
from django.utils import timezone
from .models import FinOperation, Budget, User
from financew.cron import check_and_execute_operations


class FinOperationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.budget = Budget.objects.create(amount=1000, name='Test Budget', currency='UAH', owner=self.user)
        self.operation = FinOperation.objects.create(
            budget=self.budget,
            amount=100,
            type='expense',
            time_interval='weekly',
            start_date=timezone.now(),
            is_active=True
        )

    def test_weekly_interval(self):
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=6)
        self.operation.save()
        self.assertFalse(self.operation.should_execute())  # Не повинно виконатися через 6 днів

        self.operation.last_execution = timezone.now() - timezone.timedelta(days=7)
        self.operation.save()
        self.assertTrue(self.operation.should_execute())  # Повинно виконатися через 7 днів

    def test_monthly_interval(self):
        self.operation.time_interval = 'monthly'
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=29)  # Менше 30 днів (приблизно місяць)
        self.operation.save()
        self.assertFalse(self.operation.should_execute())  # Не повинно виконатися

        self.operation.last_execution = timezone.now() - timezone.timedelta(days=31)  # Більше 30 днів
        self.operation.save()
        self.assertTrue(self.operation.should_execute())  # Повинно виконатися

    def test_yearly_interval(self):
        self.operation.time_interval = 'annually'
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=364)  # Менше 365 днів
        self.operation.save()
        self.assertFalse(self.operation.should_execute())  # Не повинно виконатися

        self.operation.last_execution = timezone.now() - timezone.timedelta(days=366)  # Більше 365 днів
        self.operation.save()
        self.assertTrue(self.operation.should_execute())  # Повинно виконатися

class FinOperationExecutionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.budget = Budget.objects.create(amount=1000, name='Test Budget', currency='UAH', owner=self.user)
        self.operation = FinOperation.objects.create(
            budget=self.budget,
            amount=100,
            type='expense',
            time_interval='weekly',
            start_date=timezone.now(),
            is_active=True
        )

    def test_weekly_execution(self):
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=7)  # Минуло 7 днів
        self.operation.save()
        initial_amount = self.budget.amount
        check_and_execute_operations()
        self.budget.refresh_from_db()  # Оновлюємо об'єкт бюджету з бази даних
        self.assertEqual(self.budget.amount, initial_amount - self.operation.amount)
        self.operation.refresh_from_db()
        self.assertIsNotNone(self.operation.last_execution)  # Перевіряємо, чи оновлено last_execution

    def test_monthly_execution(self):
        self.operation.time_interval = 'monthly'
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=31)  # Минуло 31 день
        self.operation.save()
        initial_amount = self.budget.amount
        check_and_execute_operations()
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.amount, initial_amount - self.operation.amount)
        self.operation.refresh_from_db()
        self.assertIsNotNone(self.operation.last_execution)

    def test_yearly_execution(self):
        self.operation.time_interval = 'annually'
        self.operation.last_execution = timezone.now() - timezone.timedelta(days=366)  # Минуло 366 днів
        self.operation.save()
        initial_amount = self.budget.amount
        check_and_execute_operations()
        self.budget.refresh_from_db()
        self.assertEqual(self.budget.amount, initial_amount - self.operation.amount)
        self.operation.refresh_from_db()
        self.assertIsNotNone(self.operation.last_execution)