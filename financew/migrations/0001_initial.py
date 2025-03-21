# Generated by Django 5.1.6 on 2025-03-08 10:58

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        choices=[("UAH", "UAH"), ("USD", "USD"), ("EUR", "EUR")],
                        default="UAH",
                        max_length=17,
                    ),
                ),
                ("date_added", models.DateField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "currencies",
            },
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("name", models.CharField(max_length=200, null=True)),
                (
                    "currency",
                    models.CharField(
                        choices=[("UAH", "UAH"), ("USD", "USD"), ("EUR", "EUR")],
                        default="UAH",
                        max_length=17,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "budgets",
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "categories",
            },
        ),
        migrations.CreateModel(
            name="FinOperation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=19)),
                (
                    "type",
                    models.CharField(
                        choices=[("income", "Прибуток"), ("expense", "Витрати")],
                        max_length=7,
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                (
                    "time_interval",
                    models.CharField(
                        choices=[
                            ("one_time", "Одноразовий"),
                            ("weekly", "Щотижня"),
                            ("monthly", "Щомісяця"),
                            ("annually", "Щорічно"),
                        ],
                        default="one_time",
                        max_length=17,
                    ),
                ),
                ("last_execution", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="financew.budget",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="financew.category",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "finoperations",
            },
        ),
        migrations.CreateModel(
            name="GoalBudget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=19)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "currency",
                    models.CharField(
                        choices=[("UAH", "UAH"), ("USD", "USD"), ("EUR", "EUR")],
                        default="UAH",
                        max_length=17,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "goalbudgets",
            },
        ),
        migrations.CreateModel(
            name="PeriodicStreakTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count", models.IntegerField(default=0)),
                ("date_execution", models.DateTimeField(auto_now_add=True)),
                (
                    "fin_operation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="financew.finoperation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransferBudget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                (
                    "from_budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="budget_out_set",
                        to="financew.budget",
                    ),
                ),
                (
                    "to_budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="budget_in_set",
                        to="financew.budget",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransferGoalBudget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(0.01)],
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                (
                    "from_budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="financew.budget",
                    ),
                ),
                (
                    "to_goalbudget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="financew.goalbudget",
                    ),
                ),
            ],
        ),
    ]
