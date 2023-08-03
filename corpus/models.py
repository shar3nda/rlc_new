import re

from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from natasha import Segmenter, Doc, MorphVocab, NewsEmbedding, NewsMorphTagger

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")
_RE_SPAN_PATTERN = re.compile(r"<span>.*?</span>")
# load models outside the function scope
_SEGMENTER = Segmenter()
_MORPH_VOCAB = MorphVocab()
_EMB = NewsEmbedding()
_MORPH_TAGGER = NewsMorphTagger(_EMB)


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

    @receiver(post_save)
    def update_document_annotators(sender, instance, created, **kwargs):
        # Check for the signal_sender argument
        if kwargs.get("signal_sender", True):
            Annotation = apps.get_model("corpus", "Annotation")
            if created and sender == Annotation:
                instance.document.annotators.add(instance.user)

    @transaction.atomic
    def save(self, signal_sender=True, *args, **kwargs):
        if self.pk:
            old_document = Document.objects.only("body").get(pk=self.pk)
            body_changed = old_document.body != self.body
        else:
            body_changed = True

        super(Document, self).save(*args, **kwargs)

        post_save.send(
            sender=self.__class__,
            instance=self,
            created=not bool(self.pk),
            signal_sender=signal_sender,
        )

        if body_changed and signal_sender:
            self.body = _RE_COMBINE_WHITESPACE.sub(" ", self.body).strip()
            doc = Doc(self.body)
            doc.segment(_SEGMENTER)
            doc.tag_morph(_MORPH_TAGGER)

            # lemmatize all tokens
            for token in doc.tokens:
                token.lemmatize(_MORPH_VOCAB)

            # Create Sentence objects
            sentences_bulk = []
            tokens_bulk = []

            for sentence_num, sentence in enumerate(doc.sents):
                text = sentence.text
                markup = sentence.text
                replacements = []
                offset = 0
                if hasattr(sentence.tokens[0], "start"):
                    offset = sentence.tokens[0].start

                for token in sentence.tokens:
                    feats_markup = "\n".join(
                        [
                            f"<div class='col-6'><strong>{key}:</strong></div><div class='col-6'>{value}</div>"
                            for key, value in token.feats.items()
                        ]
                    )

                    replacements.append(
                        (
                            getattr(token, "start", 1) - offset,
                            getattr(token, "end", token.start + len(token.text))
                            - offset,
                            f"""<span data-toggle="tooltip" data-bs-html="true" data-bs-original-title="
                            <div class='row'>
                                <div class='col-6'><strong>Lemma:</strong></div>
                                <div class='col-6'>{token.lemma}</div>
                            </div>
                            <div class='row'>
                                <div class='col-6'><strong>POS:</strong></div>
                                <div class='col-6'>{token.pos}</div>
                            </div>
                            <div class='row'>
                                {feats_markup}
                            </div>
                        ">{token.text}</span>""",
                        )
                    )

                replacements.sort(key=lambda x: x[1], reverse=True)
                for start, end, replacement in replacements:
                    markup = markup[:start] + replacement + markup[end:]

                sentences_bulk.append(
                    Sentence(
                        document=self, text=text, markup=markup, number=sentence_num
                    )
                )

                lemmas = []
                for token_num, token in enumerate(sentence.tokens):
                    feats = token.feats or {}
                    tokens_bulk.append(
                        Token(
                            document=self,
                            sentence_num=sentence_num,
                            sentence=sentences_bulk[-1],
                            token_num=token_num + 1,
                            token=token.text if token.text else 1,
                            lemma=token.lemma,
                            pos=token.pos,
                            animacy=feats.get("Animacy"),
                            aspect=feats.get("Aspect"),
                            case=feats.get("Case"),
                            degree=feats.get("Degree"),
                            foreign=feats.get("Foreign"),
                            gender=feats.get("Gender"),
                            hyph=feats.get("Hyph"),
                            mood=feats.get("Mood"),
                            gram_number=feats.get("Number"),
                            person=feats.get("Person"),
                            polarity=feats.get("Polarity"),
                            tense=feats.get("Tense"),
                            variant=feats.get("Variant"),
                            verb_form=feats.get("VerbForm"),
                            voice=feats.get("Voice"),
                        )
                    )
                    lemmas.append(token.lemma)

                sentences_bulk[-1].lemmas = lemmas

            Sentence.objects.bulk_create(sentences_bulk)
            Token.objects.bulk_create(tokens_bulk)

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
    A sentence is a part of a document.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, verbose_name=_("Document")
    )
    text = models.TextField(verbose_name=_("Text"))
    markup = models.TextField(null=True, blank=True, verbose_name=_("Markup"))
    number = models.IntegerField(verbose_name=_("Position in text"))
    lemmas = ArrayField(models.CharField(max_length=200), default=list)

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


def get_orig_text(annotation_json):
    target = annotation_json.get("target", {})
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
        to="corpus.Token", verbose_name=_("Tokens"), blank=True
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
            sentence=self.sentence, start__gte=self.start, end__lte=self.end
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
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    start = models.IntegerField(null=True, blank=True)
    end = models.IntegerField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    pos = models.CharField(
        max_length=10, choices=POS.choices, null=True, blank=True, db_index=True
    )
    lemma = models.CharField(null=True, blank=True, db_index=True)
    animacy = models.CharField(
        max_length=4, choices=Animacy.choices, null=True, blank=True, db_index=True
    )
    aspect = models.CharField(
        max_length=4, choices=Aspect.choices, null=True, blank=True, db_index=True
    )
    case = models.CharField(
        max_length=3, choices=Case.choices, null=True, blank=True, db_index=True
    )
    degree = models.CharField(
        max_length=3, choices=Degree.choices, null=True, blank=True, db_index=True
    )
    foreign = models.CharField(
        max_length=3, choices=Foreign.choices, null=True, blank=True, db_index=True
    )
    gender = models.CharField(
        max_length=4, choices=Gender.choices, null=True, blank=True, db_index=True
    )
    hyph = models.CharField(
        max_length=3, choices=Hyph.choices, null=True, blank=True, db_index=True
    )
    mood = models.CharField(
        max_length=3, choices=Mood.choices, null=True, blank=True, db_index=True
    )
    gram_number = models.CharField(
        max_length=4, choices=Number.choices, null=True, blank=True, db_index=True
    )
    person = models.CharField(
        max_length=1, choices=Person.choices, null=True, blank=True, db_index=True
    )
    polarity = models.CharField(
        max_length=3, choices=Polarity.choices, null=True, blank=True, db_index=True
    )
    tense = models.CharField(
        max_length=4, choices=Tense.choices, null=True, blank=True, db_index=True
    )
    variant = models.CharField(
        max_length=5, choices=Variant.choices, null=True, blank=True, db_index=True
    )
    verb_form = models.CharField(
        max_length=4, choices=VerbForm.choices, null=True, blank=True, db_index=True
    )
    voice = models.CharField(
        max_length=4, choices=Voice.choices, null=True, blank=True, db_index=True
    )
    sentence_num = models.IntegerField(null=True, blank=True)
    token_num = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _("token")
        verbose_name_plural = _("tokens")


class Token_list:
    def __init__(self, wordform, begin, end):
        self.wordform = wordform
        self.begin = begin
        self.end = end


class Filter:
    def __init__(
        self,
        date_from,
        date_to,
        gender,
        oral,
        language_background,
        dominant_languages,
        language_level,
    ):
        if not date_from:
            date_from = 0
        self.date_from = int(date_from)
        if not date_to:
            date_to = 9999
        self.date_to = int(date_to)
        self.gender = gender
        self.oral = oral
        self.language_background = language_background
        self.dominant_languages = dominant_languages
        self.language_level = language_level
