from django import forms

from .models import Article


class ArticleForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Article
        fields = ["owner", "date", "text_rus", "text_eng"]
        widgets = {
            "owner": forms.HiddenInput(),
        }
