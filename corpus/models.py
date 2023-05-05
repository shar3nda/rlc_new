import re

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from natasha import Segmenter, Doc, MorphVocab, NewsEmbedding, NewsMorphTagger
import re

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")

    class GenderChoices(models.TextChoices):
        M = "M", "Мужской"
        F = "F", "Женский"
        O = "O", "Неизвестно"

    gender = models.CharField(
        max_length=10, choices=GenderChoices.choices, verbose_name="Пол"
    )
    program = models.CharField(max_length=255, verbose_name="Программа")

    class LanguageBackgroundChoices(models.TextChoices):
        H = "H", "Эритажный"
        F = "F", "Иностранный"

    language_background = models.CharField(
        max_length=10,
        choices=LanguageBackgroundChoices.choices,
        verbose_name="Тип носителя",
    )

    class DominantLanguageChoices(models.TextChoices):
        ABK = "abk", _("Абхазский")
        AZE = "aze", _("Азербайджанский")
        ALB = "alb", _("Албанский")
        AMH = "amh", _("Амхарский")
        ENG = "eng", _("Английский")
        ARA = "ara", _("Арабский")
        ARM = "arm", _("Армянский")
        BEN = "ben", _("Бенгальский")
        BUL = "bul", _("Болгарский")
        HUN = "hun", _("Венгерский")
        VIE = "vie", _("Вьетнамский")
        DUT = "dut", _("Голландский")
        GRE = "gre", _("Греческий")
        GEO = "geo", _("Грузинский")
        DAG = "dag", _("Дагестанский")
        DAR = "dar", _("Дари")
        HEB = "heb", _("Иврит")
        IND = "ind", _("Индонезийский")
        SPA = "spa", _("Испанский")
        ITA = "ita", _("Итальянский")
        KAZ = "kaz", _("Казахский")
        CHI = "chi", _("Китайский")
        KOR = "kor", _("Корейский")
        KUR = "kur", _("Курдский")
        KHM = "khm", _("Кхмерский")
        LAO = "lao", _("Лаосский")
        MAC = "mac", _("Македонский")
        MON = "mon", _("Монгольский")
        GER = "ger", _("Немецкий")
        NEP = "nep", _("Непальский")
        NOR = "nor", _("Норвежский")
        POR = "por", _("Португальский")
        PAS = "pas", _("Пушту")
        ROM = "rom", _("Румынский")
        SER = "ser", _("Сербский")
        SVK = "svk", _("Словацкий")
        SLO = "slo", _("Словенский")
        TAJ = "taj", _("Таджикский")
        THA = "tha", _("Тайский")
        TUR = "tur", _("Турецкий")
        TURKMEN = "turkmen", _("Туркменский")
        UZB = "uzb", _("Узбекский")
        URD = "urd", _("Урду")
        FAR = "far", _("Фарси")
        FIN = "fin", _("Финский")
        FR = "fr", _("Французский")
        HIN = "hin", _("Хинди")
        CRO = "cro", _("Хорватский")
        SHO = "sho", _("Чешский")
        SWE = "swe", _("Шведский")
        SHONA = "shona", _("Шона")
        EST = "est", _("Эстонский")
        JAP = "jap", _("Японский")

    dominant_language = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=DominantLanguageChoices.choices,
        default=DominantLanguageChoices.ENG,
        db_index=True,
        verbose_name="Родной язык",
    )

    class LanguageLevelChoices(models.TextChoices):
        NOV = "NOV", "Novice"
        NL = "NL", "Novice Low"
        NM = "NM", "Novice Middle"
        NH = "NH", "Novice High"
        A1 = "A1", "A1"
        A2 = "A2", "A2"
        INT = "INT", "Intermediate"
        IL = "IL", "Intermediate Low"
        IM = "IM", "Intermediate Middle"
        IH = "IH", "Intermediate High"
        B1 = "B1", "B1"
        B2 = "B2", "B2"
        ADV = "ADV", "Advanced"
        AL = "AL", "Advanced Low"
        AM = "AM", "Advanced Middle"
        AH = "AH", "Advanced High"
        C1 = "C1", "C1"
        C2 = "C2", "C2"

    language_level = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=LanguageLevelChoices.choices,
        db_index=True,
        verbose_name="Уровень владения языком",
    )

    favorite = models.BooleanField(default=False, verbose_name="Избранное")

    def __str__(self):
        return self.name


class Document(models.Model):
    """
    A document is a text that can be annotated.
    """

    # The title of the document
    title = models.CharField(max_length=200, verbose_name="Название")
    # The owner of the document (FK to User)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    # The date when the document was created
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Дата написания текста
    date = models.IntegerField(null=True, blank=True, verbose_name="Год написания")

    # жанр текста
    class GenreChoices(models.TextChoices):
        ANSWERS = "answers", "Ответы на вопросы"
        NONACADEMIC = "nonacademic", "Неакадемическое эссе"
        ACADEMIC = "academic", "Академическое эссе"
        BLOG = "blog", "Блог"
        LETTER = "letter", "Письмо"
        STORY = "story", "История"
        PARAPHRASE = "paraphrase", "Пересказ"
        DEFINITION = "definition", "Определение"
        BIO = "bio", "Биография"
        DESCRIPTION = "description", "Описание"
        SUMMARY = "summary", "Краткое изложение"
        OTHER = "other", "Другое"

    genre = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Жанр",
        choices=GenreChoices.choices,
        default=GenreChoices.OTHER,
    )

    # название подкорпуса
    class SubcorpusChoices(models.TextChoices):
        HSE = "HSE", "HSE"
        UNICE = "UNICE", "UNICE"
        RULEC = "RULEC", "RULEC"
        FIN = "FIN", "FIN"
        BERLIN = "BERLIN", "BERLIN"
        TOKYO = "TOKYO", "TOKYO"
        SFEDU = "SFEDU", "SFEDU"

    subcorpus = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=SubcorpusChoices.choices,
        db_index=True,
        default=SubcorpusChoices.HSE,
        verbose_name="Подкорпус",
    )

    # The text of the document
    body = models.TextField(verbose_name="Текст")

    class StatusChoices(models.IntegerChoices):
        NEW = 0, "Новый"
        ANNOTATED = 1, "Аннотированный"
        CHECKED = 2, "Проверенный"

    # The status of the document (new, annotated, checked)
    status = models.IntegerField(
        choices=StatusChoices.choices, default=0, verbose_name="Статус"
    )

    author = models.ForeignKey(
        Author, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор"
    )

    time_limit = models.BooleanField(
        default=False, verbose_name="Ограничение по времени"
    )

    oral = models.BooleanField(default=False, verbose_name="Устный текст")

    source = models.CharField(
        max_length=1000, null=True, blank=True, verbose_name="Источник"
    )

    annotators = models.ManyToManyField(
        User,
        related_name="annotated_documents",
        blank=True,
        verbose_name="Аннотаторы",
    )

    @receiver(post_save)
    def update_document_annotators(sender, instance, created, **kwargs):
        Annotation = apps.get_model("corpus", "Annotation")
        if created and sender == Annotation:
            instance.document.annotators.add(instance.user)

    @staticmethod
    def replace_word_outside_span(text, word, replacement):
        span_pattern = re.compile(r"<span[^>]*>.*?</span>", re.IGNORECASE)
        index = 0
        while True:
            match = span_pattern.search(text, index)
            if not match:
                break

            start = text.find(word, index)
            if start == -1:
                break

            if start < match.start():
                return text[:start] + replacement + text[start + len(word) :]

            index = match.end()

        start = text.find(word, index)
        if start != -1:
            return text[:start] + replacement + text[start + len(word) :]

        return text

    def save(self, *args, **kwargs):
        """
        This method overrides the default save method of the model.
        It is used to create Sentence objects for each sentence in the document.
        """

        body_changed = False

        # Check if the document exists and the body has changed
        if self.pk:
            old_document = Document.objects.get(pk=self.pk)
            if old_document.body != self.body:
                body_changed = True
        else:
            body_changed = True

        super().save(*args, **kwargs)

        if body_changed:
            Sentence.objects.filter(document=self).delete()
            Annotation.objects.filter(document=self).delete()

            self.body = _RE_COMBINE_WHITESPACE.sub(" ", self.body).strip()

            # load models
            segmenter = Segmenter()
            morph_vocab = MorphVocab()
            # TODO при желании можно заменить на эмбеддинги и тэггер из худлита
            emb = NewsEmbedding()
            morph_tagger = NewsMorphTagger(emb)
            doc = Doc(self.body)

            # tokenize the text
            doc.segment(segmenter)

            # tag morphology
            doc.tag_morph(morph_tagger)

            # lemmatize all tokens
            for token in doc.tokens:
                token.lemmatize(morph_vocab)

            # create Sentence objects
            for number, sentence in enumerate(doc.sents):
                text = sentence.text
                markup = sentence.text
                for token in sentence.tokens:
                    tooltip_title = (
                        f"Lemma: {token.lemma} POS: {token.pos} Morph: {token.feats}"
                    )
                    tooltip = f'<span data-toggle="tooltip" title="{tooltip_title}">{token.text}</span>'
                    markup = self.replace_word_outside_span(markup, token.text, tooltip)
                Sentence.objects.create(
                    document=self, text=text, markup=markup, number=number
                )

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title


class Sentence(models.Model):
    """
    A sentence is a part of a document.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name="Документ"
    )
    text = models.TextField(verbose_name="Текст")
    markup = models.TextField(null=True, blank=True, verbose_name="Разметка")
    number = models.IntegerField(verbose_name="Номер в тексте")

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
            if highliters and highliters[0]["value"]:
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

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name="Документ"
    )
    sentence = models.ForeignKey(
        Sentence, on_delete=models.CASCADE, verbose_name="Предложение"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    guid = models.CharField(
        max_length=64, unique=True, editable=False, db_index=True, verbose_name="GUID"
    )
    json = models.JSONField(verbose_name="JSON")
    alt = models.BooleanField(default=False, verbose_name="Альтернативная")

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
    pos - часть речи
    feats - грамматические характеристики
    """

    token = models.CharField(max_length=200, db_index=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()
    pos = models.CharField(max_length=10, db_index=True, null=True)
    feats = models.CharField(max_length=200, db_index=True, null=True)
    lemma = models.CharField(max_length=200, db_index=True, null=True)

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

    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    lemma = models.CharField(max_length=200, db_index=True)
    part_of_speech = models.CharField(max_length=200, db_index=True)
    grammemes = models.CharField(max_length=200, db_index=True)

    def __str__(self):
        return self.lemma + " " + self.part_of_speech + " " + self.grammemes

    class Meta:
        verbose_name = _("analysis")
        verbose_name_plural = _("analyses")
