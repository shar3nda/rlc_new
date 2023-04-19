import nltk
import subprocess
import platform
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

os = platform.system()
MYSTEM_PATH = "mystem" if os == "Linux" else "mystem.exe"


class Author(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=10, choices=[("M", "Мужской"), ("F", "Женский"), ("O", "Неизвестно")]
    )
    program = models.CharField(max_length=255)
    language_background = models.CharField(
        max_length=10, choices=[("H", "Эритажный"), ("F", "Иностранный")]
    )
    NativeChoices = (
        ("eng", "English"),
        ("nor", "Norwegian"),
        ("kor", "Korean"),
        ("ita", "Italian"),
        ("fr", "French"),
        ("ger", "German"),
        ("ser", "Serbian"),
        ("jap", "Japanese"),
        ("chi", "Chinese"),
        ("kaz", "Kazakh"),
        ("dut", "Dutch"),
        ("swe", "Swedish"),
        ("fin", "Finnish"),
        ("est", "Estonian"),
        ("por", "Portuguese"),
        ("dag", "Dagestanian"),
        ("taj", "Tajik"),
        ("far", "Farsi"),
        ("ind", "Indonesian"),
        ("mon", "Mongolian"),
        ("ben", "Bengali"),
        ("heb", "Hebrew"),
        ("tur", "Turkish"),
        ("uzb", "Uzbek"),
        ("hin", "Hindi"),
        ("ara", "Arabic"),
        ("vie", "Vietnamese"),
        ("bul", "Bulgarian"),
        ("mac", "Macedonian"),
        ("cro", "Croatian"),
        ("tha", "Thai"),
        ("lao", "Lao"),
        ("spa", "Spanish"),
        ("pas", "Pashto"),
        ("dar", "Dari"),
        ("alb", "Albanian"),
        ("sho", "Shona"),
        ("sho", "Czech"),
        ("turkmen", "Turkmen"),
        ("slo", "Slovene"),
        ("abk", "Abkhaz"),
        ("aze", "Azerbaijani"),
        ("svk", "Slovak"),
        ("hun", "Hungarian"),
        ("rom", "Romanian"),
        ("nep", "Nepali"),
        ("geo", "Georgian"),
        ("amh", "Amharic"),
        ("khm", "Khmer"),
        ("kur", "Kurdish"),
        ("urd", "Urdu"),
        ("arm", "Armenian"),
        ("gre", "Greek"),
    )
    dominant_language = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=NativeChoices,
        db_index=True,
        verbose_name=_("dominant language"),
        help_text=_("Author's dominant language"),
    )
    LevelChoices = (
        (
            "Beginner",
            (
                ("NH", _("Novice High")),
                ("NL", _("Novice Low")),
                ("NM", _("Novice Middle")),
                ("A1", _("A1")),
                ("A2", _("A2")),
            ),
        ),
        (
            "Intermediate",
            (
                ("IH", _("Intermediate High")),
                ("IL", _("Intermediate Low")),
                ("IM", _("Intermediate Middle")),
                ("B1", _("B1")),
                ("B2", _("B2")),
            ),
        ),
        (
            "Advanced",
            (
                ("AH", _("Advanced High")),
                ("AL", _("Advanced Low")),
                ("AM", _("Advanced Middle")),
                ("C1", _("C1")),
                ("C2", _("C2")),
            ),
        ),
        ("Other", _("Other")),
    )
    scale = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=LevelChoices,
        db_index=True,
        help_text=_(
            "Enter the language level of the author. Both CEFR and ACTFL scales are"
            "available.</br>Please, use the option 'Other' if neither CEFR nor ACTFL"
            " scales are applicable."
        ),
        verbose_name=_("scale"),
    )

    def __str__(self):
        return self.name


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

    # Дата написания текста
    date = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("When the text was written, e.g. 2014."),
        verbose_name=_("date"),
    )
    # жанр текста
    GenreChoices = (
        ("answers", _("Answers to questions")),
        ("nonacademic", _("Non–academic essay")),
        ("academic", _("Academic essay")),
        ("blog", _("Blog")),
        ("letter", _("Letter")),
        ("story", _("Story")),
        ("paraphrase", _("Paraphrase")),
        ("definition", _("Definition")),
        ("bio", _("Biography")),
        ("description", _("Description")),
        ("summary", _("Summary")),
        ("other", _("Other")),
    )
    genre = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("genre"),
        choices=GenreChoices,
    )

    # название подкорпуса
    SubcorpusChoices = (
        ("HSE", "HSE"),
        ("UNICE", "UNICE"),
        ("RULEC", "RULEC"),
        ("FIN", "FIN"),
        ("BERLIN", "BERLIN"),
        ("TOKYO", "TOKYO"),
        ("SFEDU", "SFEDU"),
    )
    subcorpus = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Подкорпус"),
        choices=SubcorpusChoices,
    )

    # The text of the document
    body = models.TextField(help_text=_("Paste the text here."), verbose_name=_("text"))
    STATUS_CHOICES = (
        (0, _("New")),
        (1, _("Annotated")),
        (2, _("Checked")),
    )
    # The status of the document (new, annotated, checked)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    author = models.ForeignKey(Author, db_index=True, on_delete=models.PROTECT)

    source = models.TextField(
        help_text=_(
            "Name, surname and affiliation (institute, university or"
            "language school) of a person who provided the text"
        ),
        verbose_name=_("Source"),
    )

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
