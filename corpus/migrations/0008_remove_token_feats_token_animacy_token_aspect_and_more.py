# Generated by Django 4.2.1 on 2023-05-15 11:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0007_remove_author_language_level_remove_document_source_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="token",
            name="feats",
        ),
        migrations.AddField(
            model_name="token",
            name="animacy",
            field=models.CharField(
                blank=True,
                choices=[("Anim", "Anim"), ("Inan", "Inan")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="aspect",
            field=models.CharField(
                blank=True,
                choices=[("Imp", "Imp"), ("Perf", "Perf")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="case",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Acc", "Acc"),
                    ("Dat", "Dat"),
                    ("Gen", "Gen"),
                    ("Ins", "Ins"),
                    ("Loc", "Loc"),
                    ("Nom", "Nom"),
                    ("Par", "Par"),
                    ("Voc", "Voc"),
                ],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="degree",
            field=models.CharField(
                blank=True,
                choices=[("Cmp", "Cmp"), ("Pos", "Pos"), ("Sup", "Sup")],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="foreign",
            field=models.CharField(
                blank=True,
                choices=[("Yes", "Yes")],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("Fem", "Fem"), ("Masc", "Masc"), ("Neut", "Neut")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="gram_number",
            field=models.CharField(
                blank=True,
                choices=[("Plur", "Plur"), ("Sing", "Sing")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="hyph",
            field=models.CharField(
                blank=True,
                choices=[("Yes", "Yes")],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="mood",
            field=models.CharField(
                blank=True,
                choices=[("Cnd", "Cnd"), ("Imp", "Imp"), ("Ind", "Ind")],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="number",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="token",
            name="person",
            field=models.CharField(
                blank=True,
                choices=[("1", "1"), ("2", "2"), ("3", "3")],
                db_index=True,
                max_length=1,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="polarity",
            field=models.CharField(
                blank=True,
                choices=[("Neg", "Neg")],
                db_index=True,
                max_length=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="tense",
            field=models.CharField(
                blank=True,
                choices=[("Fut", "Fut"), ("Past", "Past"), ("Pres", "Pres")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="variant",
            field=models.CharField(
                blank=True,
                choices=[("Short", "Short")],
                db_index=True,
                max_length=5,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="verb_form",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Conv", "Conv"),
                    ("Fin", "Fin"),
                    ("Inf", "Inf"),
                    ("Part", "Part"),
                ],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="voice",
            field=models.CharField(
                blank=True,
                choices=[("Act", "Act"), ("Mid", "Mid"), ("Pass", "Pass")],
                db_index=True,
                max_length=4,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="dominant_language",
            field=models.CharField(
                choices=[
                    ("abk", "Abkhazian"),
                    ("aze", "Azerbaijani"),
                    ("alb", "Albanian"),
                    ("amh", "Amharic"),
                    ("eng", "English"),
                    ("ara", "Arabic"),
                    ("arm", "Armenian"),
                    ("ben", "Bengali"),
                    ("bul", "Bulgarian"),
                    ("hun", "Hungarian"),
                    ("vie", "Vietnamese"),
                    ("dut", "Dutch"),
                    ("gre", "Greek"),
                    ("geo", "Georgian"),
                    ("dag", "Daghestanian"),
                    ("dar", "Dari"),
                    ("heb", "Hebrew"),
                    ("ind", "Indonesian"),
                    ("spa", "Spanish"),
                    ("ita", "Italian"),
                    ("kaz", "Kazakh"),
                    ("chi", "Chinese"),
                    ("kor", "Korean"),
                    ("kur", "Kurdish"),
                    ("khm", "Khmer"),
                    ("lao", "Lao"),
                    ("mac", "Macedonian"),
                    ("mon", "Mongolian"),
                    ("ger", "German"),
                    ("nep", "Nepali"),
                    ("nor", "Norwegian"),
                    ("por", "Portuguese"),
                    ("pas", "Pashto"),
                    ("rom", "Romanian"),
                    ("ser", "Serbian"),
                    ("svk", "Slovak"),
                    ("slo", "Slovenian"),
                    ("taj", "Tajik"),
                    ("tha", "Thai"),
                    ("tur", "Turkish"),
                    ("turkmen", "Turkmen"),
                    ("uzb", "Uzbek"),
                    ("urd", "Urdu"),
                    ("far", "Farsi"),
                    ("fin", "Finnish"),
                    ("fr", "French"),
                    ("hin", "Hindi"),
                    ("cro", "Croatian"),
                    ("sho", "Czech"),
                    ("swe", "Swedish"),
                    ("shona", "Shona"),
                    ("est", "Estonian"),
                    ("jap", "Japanese"),
                ],
                db_index=True,
                default="eng",
                max_length=10,
                null=True,
                verbose_name="Dominant language",
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="program",
            field=models.CharField(max_length=255, verbose_name="Program"),
        ),
        migrations.AlterField(
            model_name="token",
            name="end",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="token",
            name="lemma",
            field=models.CharField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="token",
            name="pos",
            field=models.CharField(
                blank=True,
                choices=[
                    ("ADJ", "ADJ"),
                    ("ADP", "ADP"),
                    ("ADV", "ADV"),
                    ("AUX", "AUX"),
                    ("CCONJ", "CCONJ"),
                    ("DET", "DET"),
                    ("INTJ", "INTJ"),
                    ("NOUN", "NOUN"),
                    ("NUM", "NUM"),
                    ("PART", "PART"),
                    ("PRON", "PRON"),
                    ("PROPN", "PROPN"),
                    ("PUNCT", "PUNCT"),
                    ("SCONJ", "SCONJ"),
                    ("SYM", "SYM"),
                    ("VERB", "VERB"),
                    ("X", "X"),
                ],
                db_index=True,
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="token",
            name="start",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name="Morphology",
        ),
    ]