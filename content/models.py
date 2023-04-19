from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Article(models.Model):
    """A class for news articles."""

    owner = models.ForeignKey(
        User, db_index=True, blank=True, null=True, on_delete=models.PROTECT
    )
    date = models.DateField(
        help_text="Выберите",
        verbose_name=_("date"),
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    text_rus = models.TextField(
        help_text=_("Please enter the news text in Russian."),
        verbose_name=_("text in Russian"),
    )
    text_eng = models.TextField(
        help_text=_("Please enter the news text in English."),
        verbose_name=_("text in English"),
    )

    def __str__(self):
        return self.text_rus

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")


class Section(models.Model):
    """A class for storing the sections of the main page."""

    text_rus = models.TextField(
        help_text=_("Please enter the news text in Russian."),
        verbose_name=_("text in Russian"),
    )
    text_eng = models.TextField(
        help_text=_("Please enter the news text in English."),
        verbose_name=_("text in English"),
    )
    header_rus = models.CharField(
        max_length=100,
        help_text=_("Enter the name of the section in Russian"),
        verbose_name=_("name in Russian"),
    )
    header_eng = models.CharField(
        max_length=100,
        help_text=_("Enter the name of the section in English"),
        verbose_name=_("name in English"),
    )
    number = models.IntegerField(
        help_text=_("Please enter the number of the entry on the page"),
        verbose_name=_("entry number"),
    )

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")

    def __unicode__(self):
        return self.header_rus
