"""Utility functions for processing and saving Document objects.

Type hints are ommited in this module because Django models are not available at import time.
"""

import re

from django.apps import apps
from django.contrib.postgres.search import SearchVector
from django.db.models import Func, F
from django.db.models.signals import post_save

from natasha import Segmenter, Doc, MorphVocab, NewsEmbedding, NewsMorphTagger

# compiled regex constants
_RE_COMBINE_WHITESPACE = re.compile(r"\s+")
_RE_SPAN_PATTERN = re.compile(r"<span>.*?</span>")

# Natasha constants
_SEGMENTER = Segmenter()
_MORPH_VOCAB = MorphVocab()
_EMB = NewsEmbedding()
_MORPH_TAGGER = NewsMorphTagger(_EMB)


def send_post_save_signal(document):
    """Sends a post_save signal for a Document object.

    Args:
        document: Document object.
    """
    post_save.send(
        sender=document.__class__,
        instance=document,
        created=not bool(document.pk),
    )


def process_body_changes(document):
    """Processes a document body change and saves the document.

    This function is called when a document is saved with a different body. The
    document is re-analyzed with the Natasha library, and the new sentences and tokens
    are saved to the database. The old sentences and tokens are deleted, together with
    any annotations that were created in the document.

    Args:
        document: Document object.
    """
    _delete_related_objects(document)
    _process_and_save_document(document)


def _delete_related_objects(document):
    """Deletes sentences, tokens, and annotations related to a document.

    Args:
        document: Document object.
    """
    document.sentence_set.all().delete()
    document.token_set.all().delete()
    document.annotation_set.all().delete()


def _process_and_save_document(document):
    """Re-analyzes a document and saves the new sentences and tokens.

    This function processes the document body with the Natasha library and saves the
    new sentences and tokens to the database.

    Args:
        document: Document object.
    """
    document.body = _RE_COMBINE_WHITESPACE.sub(" ", document.body).strip()
    natasha_doc = Doc(document.body)
    natasha_doc.segment(_SEGMENTER)
    natasha_doc.tag_morph(_MORPH_TAGGER)
    for token in natasha_doc.tokens:
        token.lemmatize(_MORPH_VOCAB)

    sentences_bulk, tokens_bulk = _make_sentence_and_token_objects(
        document, natasha_doc
    )

    _save_sentences_and_tokens(sentences_bulk, tokens_bulk)


def _make_sentence_and_token_objects(document, natasha_doc):
    """Returns Sentence and Token object instances from a Natasha document.

    This function creates Sentence and Token objects from a Natasha document, resolving
    additional fields such as words, lemmas and HTML markup.

    Args:
        document: Document object.
        natasha_doc: Natasha Doc object.

    Returns:
        Tuple of lists of Sentence and Token objects.
    """
    sentences_bulk, tokens_bulk = [], []
    for sentence_num, natasha_sent in enumerate(natasha_doc.sents):
        markup, replacements = _prepare_sentence_markup(natasha_sent)
        sentence_object = _create_sentence_object(
            document, natasha_sent, sentence_num, markup
        )
        sentences_bulk.append(sentence_object)
        token_objects, words, lemmas = _create_token_objects_and_extract_words_lemmas(
            document, sentence_object, natasha_sent, sentence_num
        )
        sentence_object.words = words
        sentence_object.lemmas = lemmas
        tokens_bulk.extend(token_objects)

    return sentences_bulk, tokens_bulk


def _prepare_sentence_markup(natasha_sent):
    """Creates HTML markup for a Natasha sentence with token information tooltips.

    This function prepares HTML markup with Bootstrap 5 tooltips for sentence tokens.
    The tooltips contain the token's lemmatised form, part of speech, and other
    morphological features defined in the Universal Dependencies standard.

    The markup is currently generated during NLP processing to reduce the amount of
    database queries when the document is loaded. It is also easier to generate the
    markup from a Natasha instance, since linguistic features are easily accessible
    from the Natasha token object using the `feats` attribute. However, this approach
    is not ideal since it mixes the presentation and business logic and is not flexible.

    Args:
        natasha_sent: Natasha sentence object.

    Returns:
        HTML markup of the sentence.
    """

    # TODO: consider moving the markup generation to the frontend
    # suggested approach: store a JSON object with token information in the Sentence
    # object and generate the markup in the frontend using JavaScript
    markup = natasha_sent.text
    replacements = []
    offset = 0
    if hasattr(natasha_sent.tokens[0], "start"):
        offset = natasha_sent.tokens[0].start

    for token in natasha_sent.tokens:
        feats_markup = "\n".join(
            [
                f"<div class='col-6'><strong>{key}:</strong></div><div class='col-6'>{value}</div>"
                for key, value in token.feats.items()
            ]
        )

        replacements.append(
            (
                getattr(token, "start", 1) - offset,
                getattr(token, "end", token.start + len(token.text)) - offset,
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

    return markup


def _create_sentence_object(document, natasha_sent, sentence_num, markup):
    """Creates a Sentence object from a Natasha sentence.

    This function creates a Sentence instance from a Natasha sentence. The resulting
    object does not include a search vector, which has to be created after saving the
    new Sentence.

    Args:
        document: Document object.
        natasha_sent: Natasha sentence object.
        sentence_num: Number of the sentence in the document (zero-indexed).
        markup: HTML markup of the sentence with token information tooltips.

    Returns:
        Sentence object.
    """
    Sentence = apps.get_model("corpus", "Sentence")

    return Sentence(
        document=document,
        text=natasha_sent.text,
        markup=markup,
        number=sentence_num,
        start=natasha_sent.start,
        end=natasha_sent.stop,
    )


def _create_token_objects_and_extract_words_lemmas(
    document, sentence_object, natasha_sent, sentence_num
):
    """Creates Token objects from a Natasha sentence and returns them together with
    the words and lemmas lists.

    Args:
        document: Document object.
        sentence_object: Sentence object.
        natasha_sent: Natasha sentence object.
        sentence_num: Number of the sentence in the document (zero-indexed).

    Returns:
        Tuple of lists of Token objects, words, and lemmas.
    """
    Token = apps.get_model("corpus", "Token")
    token_objects = []
    words = []
    lemmas = []
    for token_num, token in enumerate(natasha_sent.tokens):
        feats = token.feats or {}
        token_objects.append(
            Token(
                document=document,
                sentence_num=sentence_num,
                sentence=sentence_object,
                token_num=token_num + 1,
                token=token.text if token.text else "",
                lemma=token.lemma,
                pos=token.pos,
                start=getattr(token, "start", 1),
                end=getattr(token, "end", token.start + len(token.text)),
                animacy=feats.get("Animacy"),
                aspect=feats.get("Aspect"),
                case=feats.get("Case"),
                degree=feats.get("Degree"),
                foreign=feats.get("Foreign"),
                gender=feats.get("Gender"),
                hyph=feats.get("Hyph"),
                mood=feats.get("Mood"),
                number=feats.get("Number"),
                person=feats.get("Person"),
                polarity=feats.get("Polarity"),
                tense=feats.get("Tense"),
                variant=feats.get("Variant"),
                verbform=feats.get("VerbForm"),
                voice=feats.get("Voice"),
            )
        )
        if token.pos not in ["PUNCT", "SYM"]:
            words.append(token.text if token.text else "")
            lemmas.append(token.lemma)

    return token_objects, words, lemmas


def _save_sentences_and_tokens(sentences_bulk, tokens_bulk):
    """Saves Sentence and Token objects to the database and creates sentence search
    vectors.

    Args:
        sentences_bulk: List of Sentence objects.
        tokens_bulk: List of Token objects.
    """

    Sentence = apps.get_model("corpus", "Sentence")
    Token = apps.get_model("corpus", "Token")

    new_sentences = Sentence.objects.bulk_create(sentences_bulk)
    new_sentences_pks = [sentence.pk for sentence in new_sentences]
    search_vector = SearchVector(
        Func(
            F("words"),
            function="array_to_string",
            template="%(function)s(%(expressions)s, ' ')",
        ),
        weight="A",
        config="simple",
    )
    Sentence.objects.filter(pk__in=new_sentences_pks).update(
        search_vector=search_vector
    )

    Token.objects.bulk_create(tokens_bulk)
