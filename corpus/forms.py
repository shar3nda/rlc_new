from django import forms

from .models import Document, Author


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "title",
            "date",
            "genre",
            "subcorpus",
            "body",
            "source",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})


class SearchForm(forms.Form):
    query = forms.CharField(label="Запрос", max_length=1000, required=False)
    in_body = forms.BooleanField(label="Искать в тексте", required=False)
    subcorpus = forms.ChoiceField(
        label="Подкорпус",
        choices=[("", "---------")] + list(Document.SubcorpusChoices.choices),
        required=False,
    )
    author__language_background = forms.ChoiceField(
        label="Тип носителя",
        choices=[("", "---------")] + list(Author.LanguageBackgroundChoices.choices),
        required=False,
    )
    genre = forms.ChoiceField(
        label="Жанр",
        choices=[("", "---------")] + list(Document.GenreChoices.choices),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs.update({"class": "form-check-input"})
            else:
                self.fields[field].widget.attrs.update({"class": "form-control"})
