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
            name="Author",
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
                ("name", models.CharField(max_length=255)),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("M", "Мужской"),
                            ("F", "Женский"),
                            ("O", "Неизвестно"),
                        ],
                        max_length=10,
                    ),
                ),
                ("program", models.CharField(max_length=255)),
                (
                    "language_background",
                    models.CharField(
                        choices=[("H", "Эритажный"), ("F", "Иностранный")],
                        max_length=10,
                    ),
                ),
                (
                    "dominant_language",
                    models.CharField(
                        choices=[
                            ("abk", "Абхазский"),
                            ("aze", "Азербайджанский"),
                            ("alb", "Албанский"),
                            ("amh", "Амхарский"),
                            ("eng", "Английский"),
                            ("ara", "Арабский"),
                            ("arm", "Армянский"),
                            ("ben", "Бенгальский"),
                            ("bul", "Болгарский"),
                            ("hun", "Венгерский"),
                            ("vie", "Вьетнамский"),
                            ("dut", "Голландский"),
                            ("gre", "Греческий"),
                            ("geo", "Грузинский"),
                            ("dag", "Дагестанский"),
                            ("dar", "Дари"),
                            ("heb", "Иврит"),
                            ("ind", "Индонезийский"),
                            ("spa", "Испанский"),
                            ("ita", "Итальянский"),
                            ("kaz", "Казахский"),
                            ("chi", "Китайский"),
                            ("kor", "Корейский"),
                            ("kur", "Курдский"),
                            ("khm", "Кхмерский"),
                            ("lao", "Лаосский"),
                            ("mac", "Македонский"),
                            ("mon", "Монгольский"),
                            ("ger", "Немецкий"),
                            ("nep", "Непальский"),
                            ("nor", "Норвежский"),
                            ("por", "Португальский"),
                            ("pas", "Пушту"),
                            ("rom", "Румынский"),
                            ("ser", "Сербский"),
                            ("svk", "Словацкий"),
                            ("slo", "Словенский"),
                            ("taj", "Таджикский"),
                            ("tha", "Тайский"),
                            ("tur", "Турецкий"),
                            ("turkmen", "Туркменский"),
                            ("uzb", "Узбекский"),
                            ("urd", "Урду"),
                            ("far", "Фарси"),
                            ("fin", "Финский"),
                            ("fr", "Французский"),
                            ("hin", "Хинди"),
                            ("cro", "Хорватский"),
                            ("sho", "Чешский"),
                            ("swe", "Шведский"),
                            ("shona", "Шона"),
                            ("est", "Эстонский"),
                            ("jap", "Японский"),
                        ],
                        db_index=True,
                        default="eng",
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "language_level",
                    models.CharField(
                        choices=[
                            (
                                "Beginner",
                                (
                                    ("NL", "Novice Low"),
                                    ("NM", "Novice Middle"),
                                    ("NH", "Novice High"),
                                    ("A1", "A1"),
                                    ("A2", "A2"),
                                ),
                            ),
                            (
                                "Intermediate",
                                (
                                    ("IL", "Intermediate Low"),
                                    ("IM", "Intermediate Middle"),
                                    ("IH", "Intermediate High"),
                                    ("B1", "B1"),
                                    ("B2", "B2"),
                                ),
                            ),
                            (
                                "Advanced",
                                (
                                    ("AL", "Advanced Low"),
                                    ("AM", "Advanced Middle"),
                                    ("AH", "Advanced High"),
                                    ("C1", "C1"),
                                    ("C2", "C2"),
                                ),
                            ),
                            ("Other", "Other"),
                        ],
                        db_index=True,
                        max_length=10,
                        null=True,
                    ),
                ),
                ("favorite", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Document",
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
                ("title", models.CharField(max_length=200)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("date", models.IntegerField(blank=True, null=True)),
                (
                    "genre",
                    models.CharField(
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
                        default="other",
                        max_length=100,
                        null=True,
                        verbose_name="genre",
                    ),
                ),
                (
                    "subcorpus",
                    models.CharField(
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
                        db_index=True,
                        default="HSE",
                        max_length=10,
                        null=True,
                    ),
                ),
                ("body", models.TextField()),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Новый"),
                            (1, "Аннотированный"),
                            (2, "Проверенный"),
                        ],
                        default=0,
                    ),
                ),
                ("source", models.CharField(max_length=1000)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.author",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_on"],
            },
        ),
        migrations.CreateModel(
            name="Sentence",
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
                ("text", models.TextField()),
                ("markup", models.TextField(blank=True, null=True)),
                ("number", models.IntegerField()),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.document",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Token",
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
                ("token", models.CharField(db_index=True, max_length=200)),
                ("start", models.IntegerField()),
                ("end", models.IntegerField()),
                ("pos", models.CharField(db_index=True, max_length=10, null=True)),
                ("feats", models.CharField(db_index=True, max_length=200, null=True)),
                ("lemma", models.CharField(db_index=True, max_length=200, null=True)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.document",
                    ),
                ),
                (
                    "sentence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.sentence",
                    ),
                ),
            ],
            options={
                "verbose_name": "token",
                "verbose_name_plural": "tokens",
            },
        ),
        migrations.CreateModel(
            name="Morphology",
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
                ("lemma", models.CharField(db_index=True, max_length=200)),
                ("part_of_speech", models.CharField(db_index=True, max_length=200)),
                ("grammemes", models.CharField(db_index=True, max_length=200)),
                (
                    "token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="corpus.token"
                    ),
                ),
            ],
            options={
                "verbose_name": "analysis",
                "verbose_name_plural": "analyses",
            },
        ),
        migrations.CreateModel(
            name="Annotation",
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
                    "guid",
                    models.CharField(
                        db_index=True, editable=False, max_length=64, unique=True
                    ),
                ),
                ("json", models.JSONField()),
                ("alt", models.BooleanField(default=False)),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.document",
                    ),
                ),
                (
                    "sentence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="corpus.sentence",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
