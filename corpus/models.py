import re

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from natasha import Segmenter, Doc, MorphVocab, NewsEmbedding, NewsMorphTagger

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Author name"))

    class GenderChoices(models.TextChoices):
        M = "M", _("Male")
        F = "F", _("Female")
        O = "O", _("Other")

    gender = models.CharField(
        max_length=10, choices=GenderChoices.choices, verbose_name=_("Gender")
    )
    program = models.CharField(max_length=255, verbose_name=_("Program"))

    class LanguageBackgroundChoices(models.TextChoices):
        H = "H", _("Heritage")
        F = "F", _("Foreign")
        O = "O", _("Other")

    language_background = models.CharField(
        max_length=10,
        choices=LanguageBackgroundChoices.choices,
        verbose_name=_("Language background"),
    )

    class DominantLanguageChoices(models.TextChoices):
        ABK = "abk", _("Abkhazian")
        AZE = "aze", _("Azerbaijani")
        ALB = "alb", _("Albanian")
        AMH = "amh", _("Amharic")
        ENG = "eng", _("English")
        ARA = "ara", _("Arabic")
        ARM = "arm", _("Armenian")
        BEN = "ben", _("Bengali")
        BUL = "bul", _("Bulgarian")
        HUN = "hun", _("Hungarian")
        VIE = "vie", _("Vietnamese")
        DUT = "dut", _("Dutch")
        GRE = "gre", _("Greek")
        GEO = "geo", _("Georgian")
        DAG = "dag", _("Daghestanian")
        DAR = "dar", _("Dari")
        HEB = "heb", _("Hebrew")
        IND = "ind", _("Indonesian")
        SPA = "spa", _("Spanish")
        ITA = "ita", _("Italian")
        KAZ = "kaz", _("Kazakh")
        CHI = "chi", _("Chinese")
        KOR = "kor", _("Korean")
        KUR = "kur", _("Kurdish")
        KHM = "khm", _("Khmer")
        LAO = "lao", _("Lao")
        MAC = "mac", _("Macedonian")
        MON = "mon", _("Mongolian")
        GER = "ger", _("German")
        NEP = "nep", _("Nepali")
        NOR = "nor", _("Norwegian")
        POR = "por", _("Portuguese")
        PAS = "pas", _("Pashto")
        ROM = "rom", _("Romanian")
        SER = "ser", _("Serbian")
        SVK = "svk", _("Slovak")
        SLO = "slo", _("Slovenian")
        TAJ = "taj", _("Tajik")
        THA = "tha", _("Thai")
        TUR = "tur", _("Turkish")
        TURKMEN = "turkmen", _("Turkmen")
        UZB = "uzb", _("Uzbek")
        URD = "urd", _("Urdu")
        FAR = "far", _("Farsi")
        FIN = "fin", _("Finnish")
        FR = "fr", _("French")
        HIN = "hin", _("Hindi")
        CRO = "cro", _("Croatian")
        SHO = "sho", _("Czech")
        SWE = "swe", _("Swedish")
        SHONA = "shona", _("Shona")
        EST = "est", _("Estonian")
        JAP = "jap", _("Japanese")

    dominant_language = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=DominantLanguageChoices.choices,
        default=DominantLanguageChoices.ENG,
        db_index=True,
        verbose_name=_("Dominant language"),
    )

    favorite = models.BooleanField(default=False, verbose_name=_("Favourites"))

    source = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Source")
    )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "program": self.program,
            "language_background": self.language_background,
            "dominant_language": self.dominant_language,
            "source": self.source
        }


class Document(models.Model):
    """
    A document is a text that can be annotated.
    """

    # The title of the document
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    # The owner of the document (FK to User)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    # The date when the document was created
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Created on"))

    # Дата написания текста
    date = models.IntegerField(null=True, blank=True, verbose_name=_("Written in"))

    # жанр текста
    class GenreChoices(models.TextChoices):
        ANSWERS = "answers", _("Answers to questions")
        NONACADEMIC = "nonacademic", _("Non–academic essay")
        ACADEMIC = "academic", _("Academic essay")
        BLOG = "blog", _("Blog")
        LETTER = "letter", _("Letter")
        STORY = "story", _("Story")
        PARAPHRASE = "paraphrase", _("Paraphrase")
        DEFINITION = "definition", _("Definition")
        BIO = "bio", _("Biography")
        DESCRIPTION = "description", _("Description")
        SUMMARY = "summary", _("Summary")
        OTHER = "other", _("Other")

    genre = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Genre"),
        choices=GenreChoices.choices,
        default=GenreChoices.OTHER,
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
        UNK = "UNK", "Unknown"

    language_level = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=LanguageLevelChoices.choices,
        db_index=True,
        verbose_name=_("Language level"),
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
        verbose_name=_("Subcorpus"),
    )

    # The text of the document
    body = models.TextField(verbose_name=_("Text"))

    class StatusChoices(models.IntegerChoices):
        NEW = 0, _("New")
        ANNOTATED = 1, _("Annotated")
        CHECKED = 2, _("Checked")

    # The status of the document (new, annotated, checked)
    status = models.IntegerField(
        choices=StatusChoices.choices, default=0, verbose_name=_("Status")
    )

    author = models.ForeignKey(
        Author,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
    )

    time_limit = models.BooleanField(default=False, verbose_name=_("Time limit"))

    oral = models.BooleanField(default=False, verbose_name=_("Oral"))

    annotators = models.ManyToManyField(
        User,
        related_name="annotated_documents",
        blank=True,
        verbose_name=_("Annotators"),
    )

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "user": self.user.username if self.user else None,
            "created_on": self.created_on.isoformat(),
            "date": self.date,
            "genre": self.genre,
            "subcorpus": self.subcorpus,
            "body": self.body,
            "status": self.get_status_display(),
            "author": self.author.serialize() if self.author else None,
            "time_limit": self.time_limit,
            "oral": self.oral,
            "language_level": self.language_level,
            "annotators": [annotator.username for annotator in self.annotators.all()],
            "sentences": [sentence.serialize() for sentence in self.sentence_set.all()],
        }

    @receiver(post_save)
    def update_document_annotators(sender, instance, created, **kwargs):
        Annotation = apps.get_model("corpus", "Annotation")
        if created and sender == Annotation:
            instance.document.annotators.add(instance.user)

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
            for sentence_num, sentence in enumerate(doc.sents):
                text = sentence.text
                markup = []
                for token in sentence.tokens:
                    tooltip_title = (
                        f"Lemma: {token.lemma} POS: {token.pos} Morph: {token.feats}"
                    )
                    tooltip = f'<span data-toggle="tooltip" title="{tooltip_title}">{token.text}</span>'
                    markup.append(tooltip)
                markup = " ".join(markup)
                new_sentence = Sentence.objects.create(
                    document=self, text=text, markup=markup, number=sentence_num
                )
                for token_num, token in enumerate(sentence.tokens):
                    Token.objects.create(
                        document=self,
                        sentence=new_sentence,
                        number=token_num,
                        start=token.start if hasattr(token, "start") else 1,
                        end=token.end if hasattr(token, "end") else token.start + len(token.text),
                        token=token.text if token.text else 1,
                        lemma=token.lemma,
                        pos=token.pos,
                        feats=token.feats,
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
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    text = models.TextField(verbose_name=_("Text"))
    markup = models.TextField(null=True, blank=True, verbose_name=_("Markup"))
    number = models.IntegerField(verbose_name=_("Position in text"))

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
                    + corrected_text[correction["end"]:]
            )

        return corrected_text

    def serialize(self):
        return {
            "text": self.text,
            "markup": self.markup,
            "number": self.number,
            "annotations": [
                annotation.serialize() for annotation in self.annotation_set.all()
            ],
        }

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
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    sentence = models.ForeignKey(
        Sentence, on_delete=models.CASCADE, verbose_name=_("Sentence")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    guid = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name=_("GUID"),
    )
    json = models.JSONField(verbose_name="JSON")
    alt = models.BooleanField(default=False, verbose_name="Альтернативная")

    def serialize(self):
        result = self.json
        result["alt"] = self.alt
        result["user"] = self.user.username
        return result

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
    number - номер слова в предложении
    pos - часть речи
    feats - грамматические характеристики
    """

    token = models.CharField(max_length=200, db_index=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    start = models.IntegerField()
    end = models.IntegerField()
    number = models.IntegerField()
    pos = models.CharField(max_length=10, db_index=True, null=True)
    feats = models.JSONField(db_index=True, null=True)
    lemma = models.CharField(max_length=200, db_index=True, null=True)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _("token")
        verbose_name_plural = _("tokens")
