# Generated by Django 5.1.6 on 2025-02-20 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financew", "0003_alter_budget_options_and_more"),
    ]

    operations = [
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
            ],
        ),
        migrations.AddField(
            model_name="budget",
            name="currency",
            field=models.CharField(
                choices=[("UAH", "UAH"), ("USD", "USD"), ("EUR", "EUR")],
                default="UAH",
                max_length=17,
            ),
        ),
        migrations.AddField(
            model_name="budget",
            name="name",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="finoperation",
            name="time_interval",
            field=models.CharField(
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
        migrations.AddField(
            model_name="finoperation",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="financew.category",
            ),
        ),
    ]
