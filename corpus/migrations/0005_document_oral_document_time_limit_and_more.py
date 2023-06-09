# Generated by Django 4.2 on 2023-05-05 09:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0004_alter_sentence_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="oral",
            field=models.BooleanField(default=False, verbose_name="Устный текст"),
        ),
        migrations.AddField(
            model_name="document",
            name="time_limit",
            field=models.BooleanField(
                default=False, verbose_name="Ограничение по времени"
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="language_level",
            field=models.CharField(
                choices=[
                    ("NOV", "Novice"),
                    ("NL", "Novice Low"),
                    ("NM", "Novice Middle"),
                    ("NH", "Novice High"),
                    ("A1", "A1"),
                    ("A2", "A2"),
                    ("INT", "Intermediate"),
                    ("IL", "Intermediate Low"),
                    ("IM", "Intermediate Middle"),
                    ("IH", "Intermediate High"),
                    ("B1", "B1"),
                    ("B2", "B2"),
                    ("ADV", "Advanced"),
                    ("AL", "Advanced Low"),
                    ("AM", "Advanced Middle"),
                    ("AH", "Advanced High"),
                    ("C1", "C1"),
                    ("C2", "C2"),
                ],
                db_index=True,
                max_length=10,
                null=True,
                verbose_name="Уровень владения языком",
            ),
        ),
    ]
