# Generated by Django 4.2 on 2023-04-22 09:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0006_remove_document_favorite_author_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="alt",
            field=models.BooleanField(default=False),
        ),
    ]
