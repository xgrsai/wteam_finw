# Generated by Django 5.1.6 on 2025-02-28 20:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("financew", "0003_category_unique_category_for_user"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="category",
            name="unique_category_for_user",
        ),
    ]
