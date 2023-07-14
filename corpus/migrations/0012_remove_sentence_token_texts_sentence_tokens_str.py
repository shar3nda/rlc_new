# Generated by Django 4.2.2 on 2023-07-13 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0011_sentence_token_texts"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sentence",
            name="token_texts",
        ),
        migrations.AddField(
            model_name="sentence",
            name="tokens_str",
            field=models.TextField(db_index=True, null=True),
        ),
    ]