import nltk
import subprocess
import platform
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

os = platform.system()
MYSTEM_PATH = "mystem" if os == "Linux" else "mystem.exe"


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
    STATUS_CHOICES = (
        (0, _("New")),
        (1, _("Annotated")),
        (2, _("Checked")),
    )
    # The status of the document (new, annotated, checked)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    def save(self, **kwargs):
        """
        This method overrides the default save method of the model.
        It is used to create Sentence objects for each sentence in the document.
        """
        super().save(**kwargs)
        # get sentences using nltk

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

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    text = models.TextField()
    number = models.IntegerField()

    # def save(
    #     self, force_insert=False, force_update=False, using=None, update_fields=None
    # ):
    #     """
    #     This method overrides the default save method of the model.
    #     It is used to create Token objects for each token in the sentence.
    #     """
    #     super().save(force_insert, force_update, using, update_fields)
    #     # get tokens using mystem
    #     args = (
    #         MYSTEM_PATH,
    #         "-cisd",
    #         "--format",
    #         "json",
    #         "--eng-gr",
    #     )
    #     process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    #     tokens = process.communicate(input=self.text.encode("utf-8"))[0].decode("utf-8")
    #     tokens = tokens.split("\n")
    #     tokens = [token for token in tokens if token]
    #     search_text = self.text
    #     for i, token in enumerate(tokens):
    #         lpos = search_text.find(token)
    #         rpos = lpos + len(token)
    #         Token.objects.create(
    #             token=token,
    #             document=self.document,
    #             sentence=self,
    #             start=lpos,
    #             end=rpos,
    #         )
    #         search_text = search_text[rpos:]

    @property
    def correction(self):
        """
        This method returns the corrected text of the sentence.
        """
        annotations = Annotation.objects.filter(sentence=self)
        if not annotations:
            return self.text

        corrections = []
        for annotation in annotations:
            # TODO: implement multiple corrections
            replacement = [
                correction
                for correction in annotation.json["body"]
                if correction["purpose"] == "commenting"
            ]
            if not replacement:
                continue
            replacement = replacement[0]["value"]
            selectors = annotation.json["target"]["selector"]
            text_position_selector = [
                selector
                for selector in selectors
                if selector["type"] == "TextPositionSelector"
            ][0]
            text_quote_selector = [
                selector
                for selector in selectors
                if selector["type"] == "TextQuoteSelector"
            ][0]

            corrections.append(
                {
                    "start": text_position_selector["start"] - 1,
                    "end": text_position_selector["end"] - 1,
                    "exact": text_quote_selector["exact"],
                    "replacement": replacement,
                }
            )

        corrections = sorted(corrections, key=lambda x: x["start"], reverse=True)
        corrected_text = self.text

        for correction in corrections:
            corrected_text = (
                corrected_text[: correction["start"]]
                + correction["replacement"]
                + corrected_text[correction["end"] :]
            )

        return corrected_text

    def __str__(self):
        return self.text


class Annotation(models.Model):
    """
    An annotation is a piece of text that is annotated by a user.
    """

    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    sentence = models.ForeignKey(Sentence, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    guid = models.CharField(max_length=64, unique=True, editable=False, db_index=True)
    json = models.JSONField()

    def __str__(self):
        return str(self.json)


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


class Morphology(models.Model):
    """Хранит информацию о морфологических разборах.

    Поля разбора:
    token - номер токена, к которому относится разбор
    lemma - начальная форма слова
    lex - часть речи
    gram - все прочие грамматические характеристики
    """

    token = models.ForeignKey(Token, on_delete=models.PROTECT)
    lemma = models.CharField(max_length=200, db_index=True)
    part_of_speech = models.CharField(max_length=200, db_index=True)
    grammemes = models.CharField(max_length=200, db_index=True)

    def __str__(self):
        return self.lemma + " " + self.part_of_speech + " " + self.grammemes

    class Meta:
        verbose_name = _("analysis")
        verbose_name_plural = _("analyses")
