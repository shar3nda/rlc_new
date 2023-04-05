from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    """
    A document is a text that can be annotated.
    """

    # The title of the document
    title = models.CharField(max_length=200, unique=True)
    # The owner of the document (FK to User)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        verbose_name=_("owner"),
        help_text=_(
            "This is the corpus user who uploads the text to the corpus."
            "Please, make sure that this field displays your login."
        ),
        on_delete=models.PROTECT,
    )
    # The date when the document was created
    created_on = models.DateTimeField(auto_now_add=True)
    # The text of the document
    body = models.TextField(help_text=_("Paste the text here."), verbose_name=_("text"))
    STATUS = (
        (0, _("New")),
        (1, _("Annotated")),
        (2, _("Checked")),
    )
    # The status of the document (new, annotated, checked)
    status = models.IntegerField(choices=STATUS, default=0)

    def save(self, **kwargs):
        """
        This method overrides the default save method of the model.
        It is used to create Sentence objects for each sentence in the document.
        """
        super().save(**kwargs)
        # get sentences using nltk
        import nltk

        sentences = nltk.sent_tokenize(self.body, language="russian")
        for i, sentence in enumerate(sentences):
            Sentence.objects.create(document=self, text=sentence, number=i)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title


class Sentence(models.Model):
    """
    A sentence is a part of a document.
    """

    # TODO настроить работу с текстом как со списком предложений
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    text = models.TextField()
    number = models.IntegerField()

    def __str__(self):
        return self.text


class Annotation(models.Model):
    """
    An annotation is a piece of text that is annotated by a user.
    """

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exact_selector = models.TextField()
    start_selector = models.IntegerField()
    end_selector = models.IntegerField()
    value = models.TextField()
    recogito_id = models.TextField()
    json = models.TextField()

    def __str__(self):
        return self.value


class Token(models.Model):
    """Хранит информацию о токенах.

    Поля токенов:
    token - само слово
    document - номер текста, к которому относится слово
    sentence - номер предложения, к которому относится слово
    start - начальная позиция слова в предложении
    end - конечная позиция слова в предложении
    """

    token = models.CharField(max_length=200, db_index=True)
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    sentence = models.ForeignKey(Sentence, on_delete=models.PROTECT)
    start = models.IntegerField()
    end = models.IntegerField()

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _("token")
        verbose_name_plural = _("tokens")
