# Generated by Django 4.2 on 2023-04-20 06:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="author",
            old_name="scale",
            new_name="language_level",
        ),
    ]