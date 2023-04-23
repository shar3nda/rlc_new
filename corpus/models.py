import platform

import nltk
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

os = platform.system()
MYSTEM_PATH = "mystem" if os == "Linux" else "mystem.exe"


class Author(models.Model):
    name = models.CharField(max_length=255)
    GenderChoices = (("M", "Мужской"), ("F", "Женский"), ("O", "Неизвестно"))
    gender = models.CharField(max_length=10, choices=GenderChoices)
    program = models.CharField(max_length=255)
    LanguageBackgroundChoices = (("H", "Эритажный"), ("F", "Иностранный"))
    language_background = models.CharField(
        max_length=10, choices=LanguageBackgroundChoices
    )
    DominantLanguageChoices = (
        ("abk", "Абхазский"),
        ("aze", "Азербайджанский"),
        ("alb", "Албанский"),
        ("amh", "Амхарский"),
        ("eng", "Английский"),
        ("ara", "Арабский"),
        ("arm", "Армянский"),
        ("ben", "Бенгальский"),
        ("bul", "Болгарский"),
        ("hun", "Венгерский"),
        ("vie", "Вьетнамский"),
        ("dut", "Голландский"),
        ("gre", "Греческий"),
        ("geo", "Грузинский"),
        ("dag", "Дагестанский"),
        ("dar", "Дари"),
        ("heb", "Иврит"),
        ("ind", "Индонезийский"),
        ("spa", "Испанский"),
        ("ita", "Итальянский"),
        ("kaz", "Казахский"),
        ("chi", "Китайский"),
        ("kor", "Корейский"),
        ("kur", "Курдский"),
        ("khm", "Кхмерский"),
        ("lao", "Лаосский"),
        ("mac", "Македонский"),
        ("mon", "Монгольский"),
        ("ger", "Немецкий"),
        ("nep", "Непальский"),
        ("nor", "Норвежский"),
        ("por", "Португальский"),
        ("pas", "Пушту"),
        ("rom", "Румынский"),
        ("ser", "Сербский"),
        ("svk", "Словацкий"),
        ("slo", "Словенский"),
        ("taj", "Таджикский"),
        ("tha", "Тайский"),
        ("tur", "Турецкий"),
        ("turkmen", "Туркменский"),
        ("uzb", "Узбекский"),
        ("urd", "Урду"),
        ("far", "Фарси"),
        ("fin", "Финский"),
        ("fr", "Французский"),
        ("hin", "Хинди"),
        ("cro", "Хорватский"),
        ("sho", "Чешский"),
        ("swe", "Шведский"),
        ("sho", "Шона"),
        ("est", "Эстонский"),
        ("jap", "Японский"),
    )
    dominant_language = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=DominantLanguageChoices,
        db_index=True,
    )
    LanguageLevelChoices = (
        (
            "Beginner",
            (
                ("NL", _("Novice Low")),
                ("NM", _("Novice Middle")),
                ("NH", _("Novice High")),
                ("A1", _("A1")),
                ("A2", _("A2")),
            ),
        ),
        (
            "Intermediate",
            (
                ("IL", _("Intermediate Low")),
                ("IM", _("Intermediate Middle")),
                ("IH", _("Intermediate High")),
                ("B1", _("B1")),
                ("B2", _("B2")),
            ),
        ),
        (
            "Advanced",
            (
                ("AL", _("Advanced Low")),
                ("AM", _("Advanced Middle")),
                ("AH", _("Advanced High")),
                ("C1", _("C1")),
                ("C2", _("C2")),
            ),
        ),
        ("Other", _("Other")),
    )
    language_level = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=LanguageLevelChoices,
        db_index=True,
    )

    favorite = models.BooleanField(default=False)

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
    )
    # жанр текста
    GenreChoices = (
        ("answers", "Ответы на вопросы"),
        ("nonacademic", "Неакадемическое эссе"),
        ("academic", "Академическое эссе"),
        ("blog", "Блог"),
        ("letter", "Письмо"),
        ("story", "История"),
        ("paraphrase", "Пересказ"),
        ("definition", "Определение"),
        ("bio", "Биография"),
        ("description", "Описание"),
        ("summary", "Краткое изложение"),
        ("other", "Другое"),
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
        choices=SubcorpusChoices,
    )

    # The text of the document
    body = models.TextField()
    StatusChoices = (
        (0, "Новый"),
        (1, "Аннотированный"),
        (2, "Проверенный"),
    )
    # The status of the document (new, annotated, checked)
    status = models.IntegerField(choices=StatusChoices, default=0)

    author = models.ForeignKey(
        Author,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    source = models.CharField(max_length=1000)

    def save(self, **kwargs):
        """
        This method overrides the default save method of the model.
        It is used to create Sentence objects for each sentence in the document.
        """
        super().save(**kwargs)
        # get sentences using nltk

        sentences = nltk.sent_tokenize(self.body, language="russian")
        # delete existing sentences

        Sentence.objects.filter(document=self).delete()

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

    def get_correction(self, alt=False):
        """
        This method returns the corrected text of the sentence.
        """
        annotations = Annotation.objects.filter(sentence=self, alt=alt)
        if not annotations:
            return self.text

        corrections = []
        for annotation in annotations:
            highliters = [
                body
                for body in annotation.json["body"]
                if body["purpose"] == "highlighting"
            ]
            if highliters and highliters[0]["value"] == True:
                continue
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

    @property
    def correction(self):
        return self.get_correction()

    @property
    def alt_correction(self):
        return self.get_correction(alt=True)

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
    alt = models.BooleanField(default=False)

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
