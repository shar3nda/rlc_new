class TokenSearchSequence:
    """Sequence of tokens for lexico-grammatical searches, their features and distances between them.

    This class stores a user-defined sequence of tokens, including their linguistic attributes, and min/max distances
    between consecutive tokens in the sequence.

    Distances specify the relative positions of consecutive tokens in the sequence. These distances are expressed as
    positional offsets from a given token and can be either positive or negative.

    A positive distance (e.g., +1) indicates that the second token is located immediately after the first token.
    Similarly, a distance of +2 means there is one token between the first and second tokens.

    A negative distance (e.g., -1) signifies that the second token is located immediately before the first token. A
    distance of -2 means there is one token between the second token and the first token, with the second token
    preceding the first.

    Attributes:
        wordforms (list[str]): A list of word lemmas.
        froms (list[int]): Minimum distances between consecutive tokens in the sequence, can be negative.
        tos (list[int]): Maximum distances between consecutive tokens in the sequence, can be negative.
        lexes (list[list[str]]): Lists of Universal Dependencies part-of-speech tags for each wordform.
        grammars (list[list[tuple[str, str]]]): Lists of tuples with feature-value pairs of Universal Dependencies
            grammatical features for each wordform.
        errors (list[list[str]]): Lists of RLC error tags for each wordform.
    """

    def __init__(
        self,
        wordforms: list[str],
        froms: list[int],
        tos: list[int],
        lexes: list[list[str]],
        grammars: list[list[tuple[str, str]]],
        errors: list[list[str]],
    ):
        self.wordforms = wordforms
        self.froms = froms
        self.tos = tos
        self.lexes = lexes
        self.grammars = grammars
        self.errors = errors


class SubcorpusSettings:
    """Subcorpus settings for a search request.

    This class stores settings for a user subcorpus (a subset of documents in the database) defined in a search
    request. These settings are used to filter documents in the database and to calculate the subcorpus size. The
    attributes may be None if the user did not specify them.

    Attributes:
        date_from (int | None): The starting year.
        date_to (int | None): The ending year.
        gender (str | None): Gender of the author ("M" for male, "F" for female).
        oral (bool | None): Whether the text is oral or written.
        language_background (str | None): The author's language background ("H" for heritage, "F" for foreign).
        dominant_languages (list[str] | None): A list of dominant languages as strings.
        language_level (list[str] | None): A list of language proficiency levels as strings ("NOV", "INT", "ADV" for
            general level, "A1", ..., "C2" for CEFR levels, "NL", ..., "AH" for ACTFL levels).
    """

    def __init__(
        self,
        date_from: int | None,
        date_to: int | None,
        gender: str | None,
        oral: bool | None,
        language_background: str | None,
        dominant_languages: list[str] | None,
        language_level: list[str] | None,
    ):
        self.date_from = date_from
        self.date_to = date_to
        self.gender = gender
        self.oral = oral
        self.language_background = language_background
        self.dominant_languages = dominant_languages
        self.language_level = language_level
