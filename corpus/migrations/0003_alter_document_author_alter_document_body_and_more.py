# Generated by Django 4.2 on 2023-04-20 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0002_rename_scale_author_language_level"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="corpus.author",
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="body",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="document",
            name="date",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="document",
            name="genre",
            field=models.CharField(
                blank=True,
                choices=[
                    ("answers", "Ответы на вопросы"),
                    ("nonacademic", "Неакадемическое эссе"),
                    ("academic", "Академическое эссе"),
                    ("blog", "Блог"),
                    ("letter", "Письмо"),
                    ("story", "История"),
                    ("paraphrase", "Пересказ"),
                    ("definition", "Определение"),
                    ("bio", "Биография"),
                    ("description", "Описание"),
                    ("summary", "Краткое изложение"),
                    ("other", "Другое"),
                ],
                db_index=True,
                max_length=100,
                null=True,
                verbose_name="genre",
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="source",
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="document",
            name="status",
            field=models.IntegerField(
                choices=[(0, "Новый"), (1, "Аннотированный"), (2, "Проверенный")],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="subcorpus",
            field=models.CharField(
                blank=True,
                choices=[
                    ("HSE", "HSE"),
                    ("UNICE", "UNICE"),
                    ("RULEC", "RULEC"),
                    ("FIN", "FIN"),
                    ("BERLIN", "BERLIN"),
                    ("TOKYO", "TOKYO"),
                    ("SFEDU", "SFEDU"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]