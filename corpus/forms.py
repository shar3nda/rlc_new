from django import forms

from .models import Document, Author
from django.utils.translation import gettext_lazy as _


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "title",
            "date",
            "genre",
            "subcorpus",
            "body",
            "time_limit",
            "oral",
            "language_level",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "200"}
            ),
            "date": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1000",
                    "max": "2050",
                    "step": "1",
                }
            ),
            "genre": forms.Select(attrs={"class": "form-select"}),
            "subcorpus": forms.Select(attrs={"class": "form-select"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": "10"}),
            "time_limit": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "oral": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "language_level": forms.Select(attrs={"class": "form-select"}),
        }


class NewAuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            "name",
            "gender",
            "program",
            "language_background",
            "dominant_language",
            "source",
            "favorite",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "200"}
            ),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "program": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "200"}
            ),
            "language_background": forms.Select(attrs={"class": "form-select"}),
            "dominant_language": forms.Select(attrs={"class": "form-select"}),
            "source": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "200"}
            ),
            "favorite": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "favorite": _("Add to favorites"),
        }


class FavoriteAuthorForm(forms.Form):
    selected_author = forms.ModelChoiceField(
        queryset=Author.objects.filter(favorite=True),
        label=_("Saved authors"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
