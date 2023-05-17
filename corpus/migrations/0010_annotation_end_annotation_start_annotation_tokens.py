# Generated by Django 4.2.1 on 2023-05-17 20:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0009_annotation_error_tags_annotation_orig_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="end",
            field=models.IntegerField(default=0, verbose_name="End"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="annotation",
            name="start",
            field=models.IntegerField(default=0, verbose_name="Start"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="annotation",
            name="tokens",
            field=models.ManyToManyField(
                blank=True, to="corpus.token", verbose_name="Tokens"
            ),
        ),
    ]
