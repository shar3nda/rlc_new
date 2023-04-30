# Generated by Django 4.2 on 2023-04-30 16:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Section",
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
                    "text_rus",
                    models.TextField(
                        help_text="Please enter the news text in Russian.",
                        verbose_name="text in Russian",
                    ),
                ),
                (
                    "text_eng",
                    models.TextField(
                        help_text="Please enter the news text in English.",
                        verbose_name="text in English",
                    ),
                ),
                (
                    "header_rus",
                    models.CharField(
                        help_text="Enter the name of the section in Russian",
                        max_length=100,
                        verbose_name="name in Russian",
                    ),
                ),
                (
                    "header_eng",
                    models.CharField(
                        help_text="Enter the name of the section in English",
                        max_length=100,
                        verbose_name="name in English",
                    ),
                ),
                (
                    "number",
                    models.IntegerField(
                        help_text="Please enter the number of the entry on the page",
                        verbose_name="entry number",
                    ),
                ),
            ],
            options={
                "verbose_name": "section",
                "verbose_name_plural": "sections",
            },
        ),
        migrations.CreateModel(
            name="Article",
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
                ("date", models.DateField(help_text="Выберите", verbose_name="date")),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "text_rus",
                    models.TextField(
                        help_text="Please enter the news text in Russian.",
                        verbose_name="text in Russian",
                    ),
                ),
                (
                    "text_eng",
                    models.TextField(
                        help_text="Please enter the news text in English.",
                        verbose_name="text in English",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "article",
                "verbose_name_plural": "articles",
            },
        ),
    ]
