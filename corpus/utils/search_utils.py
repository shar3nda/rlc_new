"""Utility functions for both search types (exact match and lexico-grammatical search)."""

import json

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q, Count, QuerySet
from django.shortcuts import render

from corpus.models import (
    Document,
    Sentence,
    Token,
    Author,
)
from .lexgram_utils import lexgram_find_sentences
from .search_helper_classes import TokenSearchSequence, SubcorpusSettings


# TODO implement matching_words correctly
# TODO implement paginated search


def get_search_stats(
    sentences: QuerySet[Sentence], subcorpus_stats: dict[str, int]
) -> dict[str, int]:
    """Returns statistics for the search results.

    This function evaluates the search statistics, extending the user subcorpus
    statistics with the number of documents, sentences, and tokens in the entire corpus
    and the number of documents, sentences, and tokens in the search results.

    Args:
        sentences: QuerySet of Sentence objects.
        subcorpus_stats: Dictionary of subcorpus statistics.

    Returns:
        Dictionary of search statistics.
    """
    total_documents = Document.objects.count()
    total_sentences = Sentence.objects.count()
    total_tokens = Token.objects.count()
    found_documents_ids = sentences.values_list("document_id", flat=True).distinct()
    found_sentences_count = sentences.count()
    return {
        "total_documents": total_documents,
        "total_sentences": total_sentences,
        "total_tokens": total_tokens,
        "subcorpus_documents": subcorpus_stats["documents"],
        "subcorpus_sentences": subcorpus_stats["sentences"],
        "subcorpus_tokens": subcorpus_stats["tokens"],
        "found_documents_ids": ",".join([str(x) for x in found_documents_ids]),
        "found_sentences_count": found_sentences_count,
    }


def preprocess_exact_search(
    json_body: str,
) -> tuple[list[str], SubcorpusSettings, int, int]:
    """Preprocesses the JSON body of an exact search request.

    This function parses the JSON body of an exact search request and returns the
    normalized search query string, the evaluated SubcorpusSettings object, the page
    size, and the chunk start (the number of already processed sentences).

    Args:
        json_body: JSON body of the request.

    Returns:
        Tuple of the normalized search query string, the evaluated SubcorpusSettings
        object, the page size, and the chunk start.
    """
    data = json.loads(json_body)
    subcorpus_settings = _create_subcorpus_settings(data.get("settings", {}))

    page_size = int(data.get("page_size", 10))
    chunk_start = int(data.get("chunk_start", 1000))

    search_query = data.get("query", "").strip().split()

    return search_query, subcorpus_settings, page_size, chunk_start


def preprocess_lexgram_search(
    json_body: str,
) -> tuple[TokenSearchSequence, SubcorpusSettings, int, int]:
    """Preprocesses the JSON body of a lexico-grammatical search request.

    This function parses the JSON body of a lexico-grammatical search request and
    returns the evaluated TokenSearchSequence object, the evaluated SubcorpusSettings
    object, the page size, and the chunk start (the number of already processed
    sentences).

    Args:
        json_body: JSON body of the request.

    Returns:
        Tuple of the evaluated TokenSearchSequence object, the evaluated
        SubcorpusSettings object, the page size, and the chunk start.
    """
    data = json.loads(json_body)
    subcorpus_settings = _create_subcorpus_settings(data.get("settings", {}))

    page_size = int(data.get("page_size", 10))
    chunk_start = int(data.get("chunk_start", 1000))

    tokens = data.get("tokens", {})
    wordforms = tokens["wordform[]"]
    froms = [int(x) for x in tokens.get("from[]", [])]
    tos = [int(x) for x in tokens.get("to[]", [])]
    lexes = [_parse_union(x) for x in tokens["lex[]"]]
    grammars_values = [
        _parse_union(x) if x else [] for x in tokens.get("grammar[]", [])
    ]
    grammars = [
        [
            (Token.get_feature_name_from_value(grammar), grammar)
            for grammar in token_grammars
        ]
        for token_grammars in grammars_values
    ]
    errors = [_parse_union(x) if x else [] for x in tokens.get("errors[]", [])]

    search_seq = TokenSearchSequence(
        wordforms=wordforms,
        froms=froms,
        tos=tos,
        lexes=lexes,
        grammars=grammars,
        errors=errors,
    )

    return search_seq, subcorpus_settings, page_size, chunk_start


def perform_exact_search(
    exact_forms: list[str],
    subcorpus_settings: SubcorpusSettings,
    page_size: int,
    chunk_start=0,
) -> tuple[QuerySet[Sentence], list[str], dict[str, int], int]:
    """Performs an exact search, ignoring case and punctuation.

    This function executes a word-for-word search within a specified subcorpus, returning a set of sentences that
    exactly match the given search terms. The search is paginated and returns search results starting from the
    specified chunk start. The search ignores case and punctuation/symbols between tokens.

    Args:
        exact_forms (list[str]): A list of strings representing the exact word forms to search for.
        subcorpus_settings (SubcorpusSettings): The settings of the subcorpus to search in.
        page_size (int): The number of search results to return per page.
        chunk_start (int, optional): The starting index of the search results chunk. Defaults to zero.

    Returns:
        tuple[QuerySet[Sentence], list[str], dict[str, int], int]: A tuple containing:
            - QuerySet[Sentence]: A QuerySet of Sentence objects matching the search criteria.
            - list[str]: The list of exact forms to highlight in the search results.
            - dict[str, int]: The search statistics (corpus, user subcorpus, and search results).
            - int: The starting index of the next chunk of search results.
    """
    sentences_queryset, subcorpus_stats = _get_subcorpus_with_stats(subcorpus_settings)

    sentences_queryset = sentences_queryset.order_by("-document_id", "number")

    # prepare the PostgreSQL full-text search query
    fts_query_string = " <-> ".join(exact_forms)
    fts_query = SearchQuery(fts_query_string, config="simple", search_type="phrase")

    matching_sentences_ids = (
        sentences_queryset.annotate(rank=SearchRank("search_vector", fts_query))
        .filter(search_vector=fts_query)
        .values_list("id", flat=True)[chunk_start : chunk_start + page_size]
    )

    matching_sentences_chunk = Sentence.objects.filter(id__in=matching_sentences_ids)

    new_chunk_start = chunk_start + page_size

    return matching_sentences_chunk, list(exact_forms), subcorpus_stats, new_chunk_start


def perform_lexgram_search(
    search_seq: TokenSearchSequence,
    subcorpus_settings: SubcorpusSettings,
    page_size: int,
    chunk_start=0,
) -> tuple[QuerySet[Sentence], list[str], dict[str, int], int]:
    """Performs a lexico-grammatical search of wordforms with specified attributes and distances.

    This function executes a lexico-grammatical search within a specified subcorpus, returning a set of sentences that
    contain the specified token sequence with the specified attributes and distances between tokens. The search is
    paginated and looks for sentence matches starting from the specified chunk start.

    When searching for a sequence of tokens, punctuation and symbol tokens are ignored.

    Note that the chunk_start is handled differently for lexico-grammatical searches than for exact searches. Here, it
    is used to skip the first chunk_start sentences in the subcorpus and not in the search results.

    For more information on how the search request looks like, refer to the ```TokenSearchSequence``` documentation.

    Args:
        search_seq (TokenSearchSequence): A sequence of tokens with specified attributes for the search.
        subcorpus_settings (SubcorpusSettings): The settings of the subcorpus to search in.
        page_size (int): The number of search results to return per page.
        chunk_start (int, optional): The starting index of the searched sentences in the subcorpus. Defaults to zero.

    Returns:
        tuple[QuerySet[Sentence], list[str], dict[str, int], int]: A tuple containing:
            - QuerySet[Sentence]: A QuerySet of Sentence objects matching the search criteria.
            - list[str]: The list of lemmas to highlight in the search results.
            - dict[str, int]: The search statistics (corpus, user subcorpus, and search results).
            - int: The starting index of the next chunk of search results.
    """
    search_seq.wordforms = [word.lower() for word in search_seq.wordforms]

    sentences, subcorpus_stats = _get_subcorpus_with_stats(subcorpus_settings)
    sentences = (
        sentences.filter(lemmas__contains=search_seq.wordforms)
        .order_by("-document_id", "number")
        .only("id")
    )

    matching_sentence_pks, matching_words, processed_count = lexgram_find_sentences(
        sentences, search_seq, chunk_start, page_size
    )

    page_sentences = Sentence.objects.filter(pk__in=matching_sentence_pks)
    return page_sentences, list(matching_words), subcorpus_stats, processed_count


def render_search_results(request, search_type):
    """Execute the search and render the results.

    This function executes the search of specified type (exact or lexico-grammatical) with the parameters specified in
    the POST request body and renders the search results. If the chunk_start parameter is non-zero, the function
    renders the next chunk of search results, otherwise it renders the initial search results with the first chunk.

    Args:
        request: The HTTP request object.
        search_type: The type of the search ("exact" or "lexgram").

    Returns:
        HttpResponse: The HTTP response object containing the rendered search results.
    """
    body = request.body

    if search_type == "lexgram":
        (
            search_sequence,
            subcorpus_settings,
            page_size,
            chunk_start,
        ) = preprocess_lexgram_search(body)

        sentences, words, subcorpus_stats, processed_count = perform_lexgram_search(
            search_sequence, subcorpus_settings, page_size, chunk_start
        )
    else:  # "exact"
        (
            search_query,
            subcorpus_settings,
            page_size,
            chunk_start,
        ) = preprocess_exact_search(body)

        sentences, words, subcorpus_stats, processed_count = perform_exact_search(
            search_query, subcorpus_settings, page_size, chunk_start
        )

    stats = get_search_stats(sentences, subcorpus_stats)

    template = "partials/search/search_results.html"
    if chunk_start > 0:
        template = "partials/search/search_results_sentences.html"

    # evaluate the queryset to apply ordering
    ordered_sentences = list(sentences.order_by("-document_id", "number"))

    return render(
        request,
        template,
        {
            "sentences": ordered_sentences,
            "stats": stats,
            "tokens_list": words,
            "is_authenticated": request.user.is_authenticated,
            "chunk_start": processed_count,
            "search_type": search_type,
            "is_last_chunk": len(ordered_sentences) < page_size,
        },
    )


def _parse_date(date_str: str | None) -> int | None:
    """Parses a date string (start/end year) into an integer.

    Args:
        date_str: The date string to parse.

    Returns:
        int | None: The parsed date as an integer or None if the string is empty or not a number.
    """

    return int(date_str) if date_str and date_str.isdigit() else None


def _parse_union(value: str | None) -> list[str]:
    """Parses a (a|b|c)-like union string into a list of strings. If there is no union, returns a one-element list.

    Args:
        value: The union string to parse.

    Returns:
        list[str]: The list of strings.
    """

    if not value:
        return []
    if "|" in value:
        return value.strip("()").split("|")
    return [value]


def _create_subcorpus_settings(settings: dict) -> SubcorpusSettings:
    """Parses the subcorpus settings from the request body into a SubcorpusSettings object.

    Args:
        settings: The subcorpus settings from the request body.

    Returns:
        SubcorpusSettings: The SubcorpusSettings object.
    """

    gender = settings.get("gender")
    if gender == "f":
        gender = "F"
    elif gender == "m":
        gender = "M"
    else:
        gender = None

    language_background = settings.get("background")
    if language_background == "heritage":
        language_background = "H"
    elif language_background == "foreign":
        language_background = "F"
    else:
        language_background = None

    text_mode = settings.get("mode")

    oral = None

    if text_mode == "oral":
        oral = True
    elif text_mode == "written":
        oral = False

    valid_dominant_languages = Author.DominantLanguageChoices.values
    dominant_languages = [
        x for x in settings.get("language[]", []) if x in valid_dominant_languages
    ]
    if not dominant_languages:
        dominant_languages = None

    valid_language_levels = Document.LanguageLevelChoices.values
    language_level = [
        x for x in settings.get("level[]", []) if x in valid_language_levels
    ]
    if not language_level:
        language_level = None

    return SubcorpusSettings(
        date_from=_parse_date(settings.get("date1")),
        date_to=_parse_date(settings.get("date2")),
        gender=gender,
        oral=oral,
        language_background=language_background,
        dominant_languages=dominant_languages,
        language_level=language_level,
    )


def _get_subcorpus_with_stats(
    subcorpus_settings: SubcorpusSettings,
) -> tuple[QuerySet[Sentence], dict[str, int]]:
    """Returns sentences found in the user-defined subcorpus and the subcorpus statistics.

    Args:
        subcorpus_settings: The settings of the subcorpus to search in.

    Returns:
        tuple[QuerySet[Sentence], dict[str, int]]: A tuple containing:
            - QuerySet[Sentence]: A QuerySet of Sentence objects in the user-defined subcorpus.
            - dict[str, int]: The subcorpus statistics (documents, sentences, and tokens).
    """
    query = Q()
    if subcorpus_settings.date_from:
        query &= Q(date__gte=subcorpus_settings.date_from) & ~Q(date__isnull=True)

    if subcorpus_settings.date_to:
        query &= Q(date__lte=subcorpus_settings.date_to) & ~Q(date__isnull=True)

    if subcorpus_settings.gender:
        query &= Q(author__gender=subcorpus_settings.gender)

    if subcorpus_settings.oral:
        query &= Q(oral=subcorpus_settings.oral)

    if subcorpus_settings.language_background:
        query &= Q(author__language_background=subcorpus_settings.language_background)

    if subcorpus_settings.dominant_languages:
        query &= Q(author__dominant_language__in=subcorpus_settings.dominant_languages)

    if subcorpus_settings.language_level:
        query &= Q(language_level__in=subcorpus_settings.language_level)

    subcorpus = Document.objects.filter(query)

    document_count = subcorpus.aggregate(Count("id"))["id__count"]
    sentence_count = Sentence.objects.filter(document__in=subcorpus).aggregate(
        Count("id")
    )["id__count"]
    token_count = Token.objects.filter(document__in=subcorpus).aggregate(Count("id"))[
        "id__count"
    ]

    subcorpus_stats = {
        "documents": document_count,
        "sentences": sentence_count,
        "tokens": token_count,
    }

    return (
        Sentence.objects.filter(document__in=subcorpus),
        subcorpus_stats,
    )
