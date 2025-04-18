# Generated by Django 5.1.4 on 2024-12-15 13:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wispapp", "0002_distribution_type_category_distribution_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Salary",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date", models.DateField()),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wispapp.member"
                    ),
                ),
            ],
        ),
    ]
