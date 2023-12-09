from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Document, Author, Token


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
            "user": forms.HiddenInput(),
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
        required=False,
    )


class TokenSearchForm(forms.ModelForm):
    GRAM_ERROR_CHOICES = [
        ("Graph", "Graph"),
        ("Hyphen", "Hyphen"),
        ("Space", "Space"),
        ("Ortho", "Ortho"),
        ("Translit", "Translit"),
        ("Misspell", "Misspell"),
        ("Deriv", "Deriv"),
        ("Infl", "Infl"),
        ("Num", "Num"),
        ("Gender", "Gender"),
        ("Morph", "Morph"),
        ("Asp", "Asp"),
        ("ArgStr", "ArgStr"),
        ("Passive", "Passive"),
        ("Refl", "Refl"),
        ("AgrNum", "AgrNum"),
        ("AgrCase", "AgrCase"),
        ("AgrGender", "AgrGender"),
        ("AgrPers", "AgrPers"),
        ("AgrGerund", "AgrGerund"),
        ("Gov", "Gov"),
        ("Ref", "Ref"),
        ("Conj", "Conj"),
        ("WO", "WO"),
        ("Neg", "Neg"),
        ("Aux", "Aux"),
        ("Brev", "Brev"),
        ("Syntax", "Syntax"),
        ("Constr", "Constr"),
        ("Lex", "Lex"),
        ("CS", "CS"),
        ("Par", "Par"),
        ("Idiom", "Idiom"),
        ("Transfer", "Transfer"),
        ("Not-clear", "Not-clear"),
        ("Del", "Del"),
        ("Insert", "Insert"),
        ("Transp", "Transp"),
        ("Subst", "Subst"),
        ("Altern", "Altern"),
        ("Tense", "Tense"),
        ("Mode", "Mode"),
    ]

    gram_errors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=GRAM_ERROR_CHOICES,
    )

    class Meta:
        model = Token
        fields = [
            "lemma",
            "pos",
            "animacy",
            "aspect",
            "case",
            "degree",
            "foreign",
            "gender",
            "hyph",
            "mood",
            "number",
            "person",
            "polarity",
            "tense",
            "variant",
            "verbform",
            "voice",
        ]
        widgets = {
            "lemma": forms.TextInput(
                attrs={"class": "form-control", "maxlength": "200"}
            ),
            "pos": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "animacy": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "aspect": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "case": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "degree": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "foreign": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "gender": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "hyph": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "mood": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "number": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "person": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "polarity": forms.Select(
                attrs={"class": "form-select", "maxlength": "200"}
            ),
            "tense": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "variant": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
            "verbform": forms.Select(
                attrs={"class": "form-select", "maxlength": "200"}
            ),
            "voice": forms.Select(attrs={"class": "form-select", "maxlength": "200"}),
        }
