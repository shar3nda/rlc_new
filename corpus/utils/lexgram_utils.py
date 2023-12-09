"""Utility functions for the lexico-grammatical search feature."""
from django.db.models import QuerySet

from corpus.models import Token, Sentence
from .search_helper_classes import TokenSearchSequence


def lexgram_find_sentences(
    sentences: QuerySet[Sentence],
    search_seq: TokenSearchSequence,
    chunk_start: int,
    page_size: int,
):
    """Finds no more than page_size sentences matching the search sequence and returns their
    primary keys.

    Args:
        sentences (QuerySet[Sentence]): A queryset of Sentence objects to search in.
        search_seq (TokenSearchSequence): A TokenSearchSequence object containing the search sequence.
        chunk_start (int): The number of sentences to skip from the beginning of the queryset.
        page_size (int): The number of search results to return per page.

    Returns:
        tuple[list[int], set[str], int]: A tuple containing:
            - list[int]: A list of sentence primary keys.
            - set[str]: A set of wordforms found in the search sequence.
            - int: The number of sentences processed.
    """

    matching_sentence_pks = []
    matching_words = set()
    processed_count = 0

    for sentence in sentences.iterator():
        if chunk_start != 0 and processed_count <= chunk_start:
            processed_count += 1
            continue

        sentence_matches = _check_sentence_match(sentence, search_seq)
        processed_count += 1

        if sentence_matches:
            matching_sentence_pks.append(sentence.pk)

        if len(matching_sentence_pks) == page_size:
            return matching_sentence_pks, matching_words, processed_count

    return matching_sentence_pks, matching_words, processed_count


def _check_sentence_match(sentence: Sentence, search_seq: TokenSearchSequence) -> bool:
    """Checks if a sentence matches the search sequence.

    Args:
        sentence (Sentence): A Sentence object to check.
        search_seq (TokenSearchSequence): A TokenSearchSequence object containing the search sequence.

    Returns:
        bool: True if the sentence matches the search sequence, False otherwise.
    """

    tokens = Token.objects.filter(sentence=sentence).exclude(pos__in=["PUNCT", "SYM"])
    seq_len = len(search_seq.wordforms)

    for token_index, token in enumerate(tokens):
        if _match_token(token, search_seq, 0) and _match_subsequent_tokens(
            tokens, token_index, search_seq, seq_len
        ):
            return True

    return False


def _match_token(token: Token, search_seq: TokenSearchSequence, seq_index: int) -> bool:
    """Matches a token against the search sequence at a given index.

    Args:
        token (Token): A Token object to match.
        search_seq (TokenSearchSequence): A TokenSearchSequence object containing the search sequence.
        seq_index (int): The index of the token in the search sequence.

    Returns:
        bool: True if the token matches the search sequence at the given index, False otherwise.
    """

    return (
        (
            (not search_seq.wordforms[seq_index])
            or token.lemma == search_seq.wordforms[seq_index]
        )
        and _check_lex(token, search_seq.lexes[seq_index])
        and _check_gram(token, search_seq.grammars[seq_index])
        and _check_errors(token, search_seq.errors[seq_index])
    )


def _match_subsequent_tokens(tokens, start_index, search_seq, seq_len):
    """Matches subsequent tokens against the search sequence.

    Args:
        tokens (QuerySet[Token]): A queryset of Token objects to match.
        start_index (int): The index of the first token to match.
        search_seq (TokenSearchSequence): A TokenSearchSequence object containing the search sequence.
        seq_len (int): The length of the search sequence.

    Returns:
        bool: True if the tokens match the search sequence, False otherwise.
    """

    prev_word_index = start_index
    for j in range(1, seq_len):
        found_match = False
        for k in range(
            max(prev_word_index + search_seq.froms[j - 1], 0),
            min(prev_word_index + search_seq.tos[j - 1] + 1, len(tokens)),
        ):
            if _match_token(tokens[k], search_seq, j):
                prev_word_index = k
                found_match = True
                break
        if not found_match:
            return False
    return True


def _check_lex(word: Token, lexes: list[str]) -> bool:
    """Check if a token's part-of-speech tag is in the list of allowed tags.

    Args:
        word (Token): A Token object to check.
        lexes (list[str]): A list of allowed part-of-speech tags.

    Returns:
        bool: True if the token's part-of-speech tag is in the list of allowed tags, False otherwise.
    """

    if not lexes:
        return True
    return word.pos in lexes


def _check_gram(word: Token, grams: list[tuple[str, str]]) -> bool:
    """Check if a token's UD grammatical features are in the list of allowed features.

    Args:
        word (Token): A Token object to check.
        grams (list[tuple[str, str]]): A list of allowed grammatical features.

    Returns:
        bool: True if the token's grammatical features are in the list of allowed features, False otherwise.
    """

    if not grams:
        return True
    for gram in grams:
        if getattr(word, gram[0]) == gram[1]:
            return True
    return False


def _check_errors(word: Token, errors: list[str]) -> bool:
    """Check if a token's RLC error tags are in the list of allowed tags.

    Args:
        word (Token): A Token object to check.
        errors (list[str]): A list of allowed RLC error tags.

    Returns:
        bool: True if the token's RLC error tags are in the list of allowed tags, False otherwise.
    """

    # TODO make a toggle for all errors at once/any error (like in RLC)
    if not errors:
        return True

    for annotation in word.annotations.all():
        if any(error in annotation.error_tags for error in errors):
            return True

    return False
