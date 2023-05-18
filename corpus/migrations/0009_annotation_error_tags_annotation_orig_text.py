# Generated by Django 4.2.1 on 2023-05-17 12:20

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0008_remove_token_feats_token_animacy_token_aspect_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="error_tags",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=64),
                blank=True,
                null=True,
                size=None,
                verbose_name="Error tags",
            ),
        ),
        migrations.AddField(
            model_name="annotation",
            name="orig_text",
            field=models.TextField(default="", verbose_name="Original text"),
            preserve_default=False,
        ),
    ]