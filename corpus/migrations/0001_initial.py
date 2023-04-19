# Generated by Django 4.2 on 2023-04-19 15:47

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
                            ("eng", "English"),
                            ("nor", "Norwegian"),
                            ("kor", "Korean"),
                            ("ita", "Italian"),
                            ("fr", "French"),
                            ("ger", "German"),
                            ("ser", "Serbian"),
                            ("jap", "Japanese"),
                            ("chi", "Chinese"),
                            ("kaz", "Kazakh"),
                            ("dut", "Dutch"),
                            ("swe", "Swedish"),
                            ("fin", "Finnish"),
                            ("est", "Estonian"),
                            ("por", "Portuguese"),
                            ("dag", "Dagestanian"),
                            ("taj", "Tajik"),
                            ("far", "Farsi"),
                            ("ind", "Indonesian"),
                            ("mon", "Mongolian"),
                            ("ben", "Bengali"),
                            ("heb", "Hebrew"),
                            ("tur", "Turkish"),
                            ("uzb", "Uzbek"),
                            ("hin", "Hindi"),
                            ("ara", "Arabic"),
                            ("vie", "Vietnamese"),
                            ("bul", "Bulgarian"),
                            ("mac", "Macedonian"),
                            ("cro", "Croatian"),
                            ("tha", "Thai"),
                            ("lao", "Lao"),
                            ("spa", "Spanish"),
                            ("pas", "Pashto"),
                            ("dar", "Dari"),
                            ("alb", "Albanian"),
                            ("sho", "Shona"),
                            ("sho", "Czech"),
                            ("turkmen", "Turkmen"),
                            ("slo", "Slovene"),
                            ("abk", "Abkhaz"),
                            ("aze", "Azerbaijani"),
                            ("svk", "Slovak"),
                            ("hun", "Hungarian"),
                            ("rom", "Romanian"),
                            ("nep", "Nepali"),
                            ("geo", "Georgian"),
                            ("amh", "Amharic"),
                            ("khm", "Khmer"),
                            ("kur", "Kurdish"),
                            ("urd", "Urdu"),
                            ("arm", "Armenian"),
                            ("gre", "Greek"),
                        ],
                        db_index=True,
                        help_text="Author's dominant language",
                        max_length=10,
                        null=True,
                        verbose_name="dominant language",
                    ),
                ),
                (
                    "scale",
                    models.CharField(
                        choices=[
                            (
                                "Beginner",
                                (
                                    ("NH", "Novice High"),
                                    ("NL", "Novice Low"),
                                    ("NM", "Novice Middle"),
                                    ("A1", "A1"),
                                    ("A2", "A2"),
                                ),
                            ),
                            (
                                "Intermediate",
                                (
                                    ("IH", "Intermediate High"),
                                    ("IL", "Intermediate Low"),
                                    ("IM", "Intermediate Middle"),
                                    ("B1", "B1"),
                                    ("B2", "B2"),
                                ),
                            ),
                            (
                                "Advanced",
                                (
                                    ("AH", "Advanced High"),
                                    ("AL", "Advanced Low"),
                                    ("AM", "Advanced Middle"),
                                    ("C1", "C1"),
                                    ("C2", "C2"),
                                ),
                            ),
                            ("Other", "Other"),
                        ],
                        db_index=True,
                        help_text="Enter the language level of the author. Both CEFR and ACTFL scales areavailable.</br>Please, use the option 'Other' if neither CEFR nor ACTFL scales are applicable.",
                        max_length=10,
                        null=True,
                        verbose_name="scale",
                    ),
                ),
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
                ("title", models.CharField(max_length=200, unique=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "date",
                    models.IntegerField(
                        blank=True,
                        help_text="When the text was written, e.g. 2014.",
                        null=True,
                        verbose_name="date",
                    ),
                ),
                (
                    "genre",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("answers", "Answers to questions"),
                            ("nonacademic", "Non–academic essay"),
                            ("academic", "Academic essay"),
                            ("blog", "Blog"),
                            ("letter", "Letter"),
                            ("story", "Story"),
                            ("paraphrase", "Paraphrase"),
                            ("definition", "Definition"),
                            ("bio", "Biography"),
                            ("description", "Description"),
                            ("summary", "Summary"),
                            ("other", "Other"),
                        ],
                        db_index=True,
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
                        max_length=100,
                        null=True,
                        verbose_name="Подкорпус",
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        help_text="Paste the text here.", verbose_name="text"
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=[(0, "New"), (1, "Annotated"), (2, "Checked")],
                        default=0,
                    ),
                ),
                (
                    "source",
                    models.TextField(
                        help_text="Name, surname and affiliation (institute, university orlanguage school) of a person who provided the text",
                        verbose_name="Source",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        help_text="This is the corpus user who uploads the text to the corpus.Please, make sure that this field displays your login.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="corpus.author",
                        verbose_name="author",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="This is the corpus user who uploads the text to the corpus.Please, make sure that this field displays your login.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="owner",
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
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="corpus.document",
                    ),
                ),
                (
                    "sentence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
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
                        on_delete=django.db.models.deletion.PROTECT, to="corpus.token"
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
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="corpus.document",
                    ),
                ),
                (
                    "sentence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="corpus.sentence",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
