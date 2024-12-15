# Generated by Django 5.1.4 on 2024-12-15 04:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wispapp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Distribution_type",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="category",
            name="distribution_type",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="wispapp.distribution_type",
            ),
        ),
    ]
