from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchVectorField,
)
from django.db import models
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .utils.document_utils import send_post_save_signal, process_body_changes


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Author name"))

    class GenderChoices(models.TextChoices):
        M = "M", _("Male")
        F = "F", _("Female")
        # noinspection PyPep8
        O = "O", _("Other")

    gender = models.CharField(
        max_length=10, choices=GenderChoices.choices, verbose_name=_("Gender")
    )
    program = models.CharField(max_length=255, verbose_name=_("Program"))

    class LanguageBackgroundChoices(models.TextChoices):
        H = "H", _("Heritage")
        F = "F", _("Foreign")
        # noinspection PyPep8
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
            "source": self.source,
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
            "annotators": list(self.annotators.values_list("username", flat=True)),
            "sentences": self.serialize_sentences(),
        }

    def serialize_sentences(self):
        sentences = self.sentence_set.all()
        return [sentence.serialize() for sentence in sentences]

    # noinspection PyMethodParameters
    @receiver(post_save)
    def update_document_annotators(sender, instance, created, **kwargs):
        # noinspection PyPep8Naming,PyShadowingNames
        Annotation = apps.get_model("corpus", "Annotation")
        if created and sender == Annotation:
            instance.document.annotators.add(instance.user)

    @transaction.atomic
    def save(self, *args, **kwargs):
        body_changed = (
            not self.pk
            or Document.objects.only("body").get(pk=self.pk).body != self.body
        )
        super().save(*args, **kwargs)
        send_post_save_signal(self)
        if body_changed:
            process_body_changes(self)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title


def get_selectors(annotation_json):
    selectors = annotation_json["target"]["selector"]
    text_position_selector = [
        selector for selector in selectors if selector["type"] == "TextPositionSelector"
    ][0]
    text_quote_selector = [
        selector for selector in selectors if selector["type"] == "TextQuoteSelector"
    ][0]
    return (
        text_position_selector.get("start"),
        text_position_selector.get("end"),
        text_quote_selector.get("exact"),
    )


class Sentence(models.Model):
    """
    Represents a single sentence as part of a document in the text corpus.

    Attributes:

    - document (ForeignKey): A reference to the associated `Document` object.
    - text (TextField): The actual text content of the sentence.
    - markup (TextField): HTML markup of the sentence, containing Bootstrap 5 tooltips with token information.
    - number (IntegerField): Indicates the position of the sentence within the document, starting from 0.
    - words (ArrayField): A list of the tokens in the sentence, excluding punctuation marks (PUNCT) and symbols (SYM).
    - lemmas (ArrayField): A list of lemmatized forms of the tokens in the sentence, excluding punctuation marks (PUNCT)
        and symbols (SYM).
    - start (IntegerField): The start position of the sentence within the full document text.
    - end (IntegerField): The end position of the sentence within the full document text.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    text = models.TextField(verbose_name=_("Text"))
    markup = models.TextField(null=True, blank=True, verbose_name=_("Markup"))
    number = models.IntegerField(verbose_name=_("Position in text"))
    words = ArrayField(models.CharField(max_length=200), default=list)
    lemmas = ArrayField(models.CharField(max_length=200), default=list)
    start = models.IntegerField(null=True, blank=True)
    end = models.IntegerField(null=True, blank=True)
    search_vector = SearchVectorField(null=True)

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
                replacement = ""
            else:
                replacement = replacement[0]["value"]

            start, end, exact = get_selectors(annotation.json)
            corrections.append(
                {
                    "start": start,
                    "end": end,
                    "exact": exact,
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

    def serialize(self):
        return {
            "text": self.text,
            "markup": self.markup,
            "number": self.number,
            "annotations": self.serialize_annotations(),
        }

    def serialize_annotations(self):
        annotations = self.annotation_set.all()
        return [annotation.serialize() for annotation in annotations]

    @property
    def correction(self):
        return self.get_correction()

    @property
    def alt_correction(self):
        return self.get_correction(alt=True)

    def __str__(self):
        return self.text

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(fields=["lemmas"]),
        ]


def get_orig_text(annotation_json):
    _, _, exact = get_selectors(annotation_json)
    return exact


def get_error_tags(annotation_json):
    body = annotation_json.get("body", [])
    error_tags = []
    for body_item in body:
        if body_item.get("purpose") == "tagging":
            error_tags.append(body_item.get("value", []))
    return error_tags


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
    orig_text = models.TextField(verbose_name=_("Original text"))
    start = models.IntegerField(verbose_name=_("Start"))
    end = models.IntegerField(verbose_name=_("End"))
    tokens = models.ManyToManyField(
        to="corpus.Token",
        related_name="annotations",
        verbose_name=_("Tokens"),
        blank=True,
    )
    error_tags = ArrayField(
        models.CharField(max_length=64, blank=True),
        blank=True,
        null=True,
        verbose_name=_("Error tags"),
    )

    # save and set orig_text and error_tags
    def save(self, *args, **kwargs):
        self.start, self.end, self.orig_text = get_selectors(self.json)
        self.error_tags = get_error_tags(self.json)
        toks = Token.objects.filter(
            sentence=self.sentence,
            start__gte=self.start + self.sentence.start,
            end__lte=self.end + self.sentence.start,
        )
        super().save(*args, **kwargs)
        self.tokens.set(toks)

    def serialize(self):
        result = self.json
        result["alt"] = self.alt
        result["user"] = self.user.username
        return result

    def __str__(self):
        return str(self.json)


class Token(models.Model):
    """Token, a single word/symbol in a sentence with its linguistic features.

    The token model represents a single word or punctuation mark in a sentence.
    It contains the actual text of the token, its lemmatized form, and its position in the sentence and document.
    It also contains the linguistic features of the token from Universal Dependencies.
    Documents and sentences are linked to tokens via foreign keys.

    Names of inner classes are the same as the names of the corresponding features in Universal Dependencies.
    Names of model attributes are lowercase versions of them.

    Attributes:
        token (str): The actual text of the token.
        lemma (str, optional): The lemmatized form of the token. Can be null or blank.
        start (int, optional): The starting position index of the token within the sentence.
        end (int, optional): The end position index of the token within the sentence.
        token_num (int, optional): The sequential position of the token in the sentence, starting from 1.
        sentence_num (int, optional): The position of the sentence that this token belongs to in the document, starting
            from 0.
        sentence (ForeignKey): A foreign key link to the Sentence model, indicating which sentence the token belongs to.
            Deletes the token if the linked sentence is deleted.
        document (ForeignKey): A foreign key link to the Document model, indicating which document the token belongs to.
            Deletes the token if the linked document is deleted.

        pos (CharField, optional): The part of speech of the token (e.g. NOUN, VERB, ADJ, etc.)
        animacy (CharField, optional): The animacy of the token.
        aspect (CharField, optional): The aspect of the token.
        case (CharField, optional): The case of the token. Includes rare cases such as Par (partitive) and Voc
            (vocative).
        degree (CharField, optional): The degree of the token.
        foreign (CharField, optional): Whether the token is a foreign word.
        gender (CharField, optional): The grammatical gender of the token.
        hyph (CharField, optional): Whether the token contains a hyphen.
        mood (CharField, optional): The mood of the token.
        number (CharField, optional): The grammatical number of the token (singular or plural).
        person (CharField, optional): The grammatical person of the token (1st, 2nd, or 3rd).
        polarity (CharField, optional): The polarity of the token (only negative in Russian).
        tense (CharField, optional): The tense of the token.
        variant (CharField, optional): The variant of the token (only Short in Russian).
        verbform (CharField, optional): The verb form of the token.
        voice (CharField, optional): The voice of the token.
    """

    class POS(models.TextChoices):
        ADJ = "ADJ", _("ADJ")
        ADP = "ADP", _("ADP")
        ADV = "ADV", _("ADV")
        AUX = "AUX", _("AUX")
        CCONJ = "CCONJ", _("CCONJ")
        DET = "DET", _("DET")
        INTJ = "INTJ", _("INTJ")
        NOUN = "NOUN", _("NOUN")
        NUM = "NUM", _("NUM")
        PART = "PART", _("PART")
        PRON = "PRON", _("PRON")
        PROPN = "PROPN", _("PROPN")
        PUNCT = "PUNCT", _("PUNCT")
        SCONJ = "SCONJ", _("SCONJ")
        SYM = "SYM", _("SYM")
        VERB = "VERB", _("VERB")
        X = "X", _("X")

    class Animacy(models.TextChoices):
        ANIM = "Anim", _("Anim")
        INAN = "Inan", _("Inan")

    class Aspect(models.TextChoices):
        IMP = "Imp", _("Imp")
        PERF = "Perf", _("Perf")

    class Case(models.TextChoices):
        ACC = "Acc", _("Acc")
        DAT = "Dat", _("Dat")
        GEN = "Gen", _("Gen")
        INS = "Ins", _("Ins")
        LOC = "Loc", _("Loc")
        NOM = "Nom", _("Nom")
        PAR = "Par", _("Par")
        VOC = "Voc", _("Voc")

    class Degree(models.TextChoices):
        CMP = "Cmp", _("Cmp")
        POS = "Pos", _("Pos")
        SUP = "Sup", _("Sup")

    class Foreign(models.TextChoices):
        YES = "Yes", _("Yes")

    class Gender(models.TextChoices):
        FEM = "Fem", _("Fem")
        MASC = "Masc", _("Masc")
        NEUT = "Neut", _("Neut")

    class Hyph(models.TextChoices):
        YES = "Yes", _("Yes")

    class Mood(models.TextChoices):
        CND = "Cnd", _("Cnd")
        IMP = "Imp", _("Imp")
        IND = "Ind", _("Ind")

    class Number(models.TextChoices):
        PLUR = "Plur", _("Plur")
        SING = "Sing", _("Sing")

    class Person(models.TextChoices):
        FIRST = "1", _("1")
        SECOND = "2", _("2")
        THIRD = "3", _("3")

    class Polarity(models.TextChoices):
        NEG = "Neg", _("Neg")

    class Tense(models.TextChoices):
        FUT = "Fut", _("Fut")
        PAST = "Past", _("Past")
        PRES = "Pres", _("Pres")

    class Variant(models.TextChoices):
        SHORT = "Short", _("Short")

    class VerbForm(models.TextChoices):
        CONV = "Conv", _("Conv")
        FIN = "Fin", _("Fin")
        INF = "Inf", _("Inf")
        PART = "Part", _("Part")

    class Voice(models.TextChoices):
        ACT = "Act", _("Act")
        MID = "Mid", _("Mid")
        PASS = "Pass", _("Pass")

    token = models.CharField(max_length=200, db_index=True)
    lemma = models.CharField(null=True, blank=True, db_index=True)
    start = models.IntegerField()
    end = models.IntegerField()
    token_num = models.IntegerField()
    sentence_num = models.IntegerField()
    sentence = models.ForeignKey(
        Sentence, related_name="tokens", on_delete=models.CASCADE, db_index=True
    )
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_index=True)

    # Universal Dependencies attributes
    pos = models.CharField(max_length=10, choices=POS.choices, db_index=True)
    animacy = models.CharField(
        max_length=4, choices=Animacy.choices, null=True, blank=True
    )
    aspect = models.CharField(
        max_length=4, choices=Aspect.choices, null=True, blank=True
    )
    case = models.CharField(max_length=3, choices=Case.choices, null=True, blank=True)
    degree = models.CharField(
        max_length=3, choices=Degree.choices, null=True, blank=True
    )
    foreign = models.CharField(
        max_length=3, choices=Foreign.choices, null=True, blank=True
    )
    gender = models.CharField(
        max_length=4, choices=Gender.choices, null=True, blank=True
    )
    hyph = models.CharField(max_length=3, choices=Hyph.choices, null=True, blank=True)
    mood = models.CharField(max_length=3, choices=Mood.choices, null=True, blank=True)
    number = models.CharField(
        max_length=4, choices=Number.choices, null=True, blank=True
    )
    person = models.CharField(
        max_length=1, choices=Person.choices, null=True, blank=True
    )
    polarity = models.CharField(
        max_length=3, choices=Polarity.choices, null=True, blank=True
    )
    tense = models.CharField(max_length=4, choices=Tense.choices, null=True, blank=True)
    variant = models.CharField(
        max_length=5, choices=Variant.choices, null=True, blank=True
    )
    verbform = models.CharField(
        max_length=4, choices=VerbForm.choices, null=True, blank=True
    )
    voice = models.CharField(max_length=4, choices=Voice.choices, null=True, blank=True)

    def __str__(self):
        return self.token

    @staticmethod
    def get_feature_name_from_value(value: str) -> str | None:
        """Retrieves the feature name corresponding to a given value.

        This method dynamically inspects the model's fields that have choices defined to find which feature the given
            value corresponds to. If the value matches any of the choices or starts with a capitalized version of the
            field name, it returns the field's name as the feature name.

        Args:
            value (str): The value for which the corresponding feature name is to be found.

        Returns:
            str | None: The name of the feature corresponding to the given value. Returns None if no matching feature is
                found.

        Examples:
            >>> token = Token()
            >>> token.get_feature_name_from_value("Cmp")
            'degree'
            >>> token.get_feature_name_from_value("ForeignYes")
            'foreign'
            >>> token.get_feature_name_from_value("UnknownValue")
            None
        """

        for field in Token._meta.get_fields():
            if hasattr(field, "choices") and isinstance(field, models.CharField):
                if not field.choices:
                    continue
                choice_map = dict(field.choices)

                if value.startswith(field.name.capitalize()):
                    return field.name

                if value in choice_map.values():
                    return field.name

        return None

    class Meta:
        verbose_name = _("token")
        verbose_name_plural = _("tokens")
