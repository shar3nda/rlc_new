""" Main collection of functions for classifying edits """
import pymorphy2
import re

from Levenshtein import ratio as lev
from nltk.stem.snowball import SnowballStemmer

ML = False  # True

if ML:
    from morph_ortho import is_morph

pymorphy_parser = pymorphy2.MorphAnalyzer()
stemmer = SnowballStemmer("russian")


def classify(edit):
    if not edit.o_toks and not edit.c_toks:
        edit.type = "UNK"
    elif not edit.o_toks and edit.c_toks:
        edit.type = get_one_sided_type(edit.c_toks)
    elif edit.o_toks and not edit.c_toks:
        edit.type = get_one_sided_type(edit.o_toks)
    else:
        if edit.o_str == edit.c_str:
            edit.type = "UNK"
        else:
            edit.type = get_two_sided_type(edit.o_toks, edit.c_toks)
    return edit


def get_one_sided_type(toks):
    if one_sided_tense(toks):
        return "Tense"
    if one_sided_mode(toks):
        return "Mode"
    if one_sided_aux(toks):
        return "Aux"
    if one_sided_conj(toks):
        return "Conj"
    if one_sided_ref(toks):
        return "Ref"
    if one_sided_prep(toks):
        return "Prep"
    if one_sided_cs(toks):
        return "CS"
    if one_sided_syntax(toks):
        return "Syntax"
    return "Lex"


def one_sided_cs(toks):
    for tok in toks:
        if tok.feats.get("Foreign") == "Yes":
            return True
    return False


def one_sided_mode(toks):
    if len(toks) == 1 and toks[0].pos == "AUX" and toks[0].feats.get("Mood") == "Cnd":
        return True
    return False


def one_sided_ref(toks):
    pos_set = {tok.pos for tok in toks}

    if pos_set.issubset({"DET", "PRON"}):
        return True
    return False


def one_sided_conj(toks):
    pos_set = {tok.pos for tok in toks}

    if pos_set.issubset({"CCONJ", "SCONJ"}):
        return True
    return False


def one_sided_aux(toks):
    if (
        (len(toks) == 1)
        and (toks[0].lemma == "быть" or toks[0].lemma == "стать")
        and (toks[0].feats.get("Tense") == "Pres")
    ):
        return True
    return False


def one_sided_tense(toks):
    if (
        (len(toks) == 1)
        and (toks[0].lemma == "быть")
        and (toks[0].feats.get("Tense") != "Pres")
    ):
        return True
    return False


def one_sided_syntax(toks):
    pos_set = {tok.pos for tok in toks}
    if pos_set.issubset({"PUNCT"}):
        return True


def one_sided_prep(toks):
    pos_set = {tok.pos for tok in toks}
    if pos_set.issubset({"ADP"}):
        return True
    return False


def one_sided_lex(toks):
    # pymorphy_parser = pymorphy2.MorphAnalyzer()
    if len(toks) == 1 and pymorphy_parser.word_is_known(toks[0].text):
        return True
    return False


def get_two_sided_type(o_toks, c_toks):
    if brev(o_toks, c_toks):
        return "Brev"
    if num(o_toks, c_toks):
        return "Num"
    if gender(o_toks, c_toks):
        return "Gender"
    if wrong_case(o_toks, c_toks):
        if noun_case(o_toks, c_toks):
            return "Nominative" if nominative(c_toks) else "Gov"
        else:
            return "Agrcase"
    if agrnum(o_toks, c_toks):
        return "Agrnum"
    # if agrcase(o_toks, c_toks):
    #    return "Agrcase"
    if agrpers(o_toks, c_toks):
        return "Agrpers"
    if agrgender(o_toks, c_toks):
        return "Agrgender"

    if tense(o_toks, c_toks):
        return "Tense"
    if passive(o_toks, c_toks):
        return "Passive"
    if refl(o_toks, c_toks):
        return "Refl"
    if asp(o_toks, c_toks):
        return "Asp"

    if impers(o_toks, c_toks):
        return "Impers"
    if com(o_toks, c_toks):
        return "Com"
    if mode(o_toks, c_toks):
        return "Mode"

    if conj(o_toks, c_toks):
        return "Conj"
    if ref(o_toks, c_toks):
        return "Ref"
    if prep(o_toks, c_toks):
        return "Prep"

    if cs(o_toks, c_toks):
        return "CS"
    if graph(o_toks, c_toks):
        return "Graph"

    if hyphen_ins(o_toks, c_toks):
        return "Hyphen+Ins"
    if hyphen_del(o_toks, c_toks):
        return "Hyphen+Del"

    if space_ins(o_toks, c_toks):
        return "Space+Ins"
    if space_del(o_toks, c_toks):
        return "Space+Del"

    if word_order(o_toks, c_toks):
        return "WO"

    if infl(o_toks, c_toks):
        return "Infl"
    if lex(o_toks, c_toks):
        return "Lex"
    if syntax(o_toks, c_toks):
        return "Syntax"

    tag = "(Morph)" if morph(o_toks, c_toks) else ""
    if morph_ml(o_toks, c_toks):
        return tag + "Morph"
    if ortho(o_toks, c_toks):
        return tag + "Ortho"

    return tag + "Misspell"


# ORTHOGRAPHY


def graph(o_toks, c_toks):
    for tok in o_toks:
        if re.search("[а-яА-Я]", tok.text) and tok.feats.get("Foreign") == "Yes":
            return True
    return False


def space_ins(o_toks, c_toks):
    o_join = "".join([o.text.lower() for o in o_toks])
    c_join = "".join([c.text.lower() for c in c_toks])
    if o_join == c_join and len(o_toks) < len(c_toks):
        return True
    return False


def space_del(o_toks, c_toks):
    o_join = "".join([o.text.lower() for o in o_toks])
    c_join = "".join([c.text.lower() for c in c_toks])
    if o_join == c_join and len(o_toks) > len(c_toks):
        return True
    return False


def hyphen_ins(o_toks, c_toks):
    o_join = "".join([o.text.lower() for o in o_toks])
    c_join = "".join([c.text.lower() for c in c_toks])
    if (
        "-" in c_join
        and "-" not in o_join
        and lev(o_join, re.sub("-", "", c_join)) >= 0.75
    ):
        return True
    return False


def hyphen_del(o_toks, c_toks):
    o_join = "".join([o.text.lower() for o in o_toks])
    c_join = "".join([c.text.lower() for c in c_toks])
    if (
        "-" in o_join
        and "-" not in c_join
        and lev(re.sub("-", "", o_join), c_join) >= 0.75
    ):
        return True
    return False


# MORPHOLOGY


def infl(o_toks, c_toks):
    if (len(o_toks) == len(c_toks) == 1) and (
        (stemmer.stem(o_toks[0].text) == stemmer.stem(c_toks[0].text))
        or (o_toks[0].lemma == c_toks[0].lemma)
    ):
        parses = pymorphy_parser.parse(c_toks[0].lemma)
        if o_toks[0].text.lower() not in [
            form.word for p in parses for form in p.lexeme
        ]:
            return True
    return False


def num(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    o_nums = [o_tok.feats.get("Number", None) for o_tok in o_toks]
    c_nums = [c_tok.feats.get("Number", None) for c_tok in c_toks]
    pos_set = {tok.pos for tok in o_toks + c_toks}
    lemmas_match_flags = [
        (o_toks[i].lemma == c_toks[i].lemma) for i in range(len(o_toks))
    ]

    if (
        (len(set(o_nums)) == len(set(c_nums)) == 1)
        and (not (None in o_nums))
        and (not (None in c_nums))
        and (o_nums != c_nums)
        and (sum(lemmas_match_flags) == len(lemmas_match_flags))
        and (len(pos_set & {"VERB", "PROPN", "NOUN", "PRON"}) > 0)
    ):
        return True

    return False


def gender(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    # o_genders = [o_tok.feats.get('Gender', None) for o_tok in o_toks]
    o_genders = [pymorphy_parser.parse(o_tok.text)[0].tag.gender for o_tok in o_toks]
    # c_genders = [c_tok.feats.get('Gender', None) for c_tok in c_toks]
    c_genders = [pymorphy_parser.parse(c_tok.text)[0].tag.gender for c_tok in c_toks]
    if (
        o_genders == c_genders
        or len(set(o_genders)) > 1
        or len(set(c_genders)) > 1
        or None in o_genders
        or None in c_genders
    ):
        return False

    stemmer = SnowballStemmer("russian")
    if not all(
        [
            (stemmer.stem(o_toks[i].lemma) == stemmer.stem(c_toks[i].lemma))
            for i in range(len(o_toks))
        ]
    ):
        return False

    pos_set = {tok.pos for tok in o_toks + c_toks}
    return len(pos_set & {"VERB", "PROPN", "NOUN", "PRON"}) > 0


# SYNTAX


def asp(o_toks, c_toks):
    if (
        (len(o_toks) == len(c_toks) == 1)
        and (o_toks[0].pos == c_toks[0].pos == "VERB")
        and
        # (o_toks[0].lemma == c_toks[0].lemma) and
        related_stems(o_toks[0].lemma, c_toks[0].lemma)
        and (o_toks[0].feats["Aspect"] != c_toks[0].feats["Aspect"])
    ):
        return True
    return False


def passive(o_toks, c_toks):
    o_pos = [o_tok.pos for o_tok in o_toks]
    c_pos = [c_tok.pos for c_tok in c_toks]
    o_voices = [o_tok.feats.get("Voice", None) for o_tok in o_toks]
    c_voices = [c_tok.feats.get("Voice", None) for c_tok in c_toks]
    if ("VERB" in o_pos and "VERB" in c_pos) and (
        ("Act" in o_voices and "Pass" in c_voices)
        or ("Pass" in o_voices and "Act" in c_voices)
    ):
        return True

    return False


def brev_natasha(o_toks, c_toks):
    for o_tok in o_toks:
        for c_tok in c_toks:
            if (
                o_tok.lemma == c_tok.lemma
                or stemmer.stem(o_tok.text) == stemmer.stem(c_tok.text)
            ) and o_tok.feats.get("Variant") != c_tok.feats.get("Variant"):
                return True
    return False


def get_adjectives(toks):
    return [
        p
        for t in toks
        for p in pymorphy_parser.parse(t.text)
        if p.tag.POS in ["ADJF", "ADJS", "PRTS", "PRTF"]
    ]


def brev(o_toks, c_toks):
    o_adjs = get_adjectives(o_toks)
    c_adjs = get_adjectives(c_toks)
    for o in o_adjs:
        for c in c_adjs:
            if o.tag.POS != c.tag.POS and (
                o.normal_form == c.normal_form
                or stemmer.stem(o.word) == stemmer.stem(c.word)
            ):
                return True
    return False


def tense(o_toks, c_toks):
    # Past <-> Present switch
    if len(o_toks) == len(c_toks) == 1:
        o_tok = o_toks[0]
        c_tok = c_toks[0]
        if (
            (o_tok.pos == c_tok.pos == "VERB")
            and ("Tense" in o_tok.feats)
            and ("Tense" in c_tok.feats)
            and (o_tok.lemma == c_tok.lemma)
            and (o_tok.feats["Tense"] != c_tok.feats["Tense"])
        ):
            return True
    # Past/Present <-> Future switch
    else:
        aux_in_o = False
        aux_in_c = False
        for tok in o_toks:
            if (
                tok.lemma == "быть"
                and tok.pos == "AUX"
                and tok.feats.get("Tense") == "Pres"
            ):
                aux_in_o = True
                break
        for tok in c_toks:
            if (
                tok.lemma == "быть"
                and tok.pos == "AUX"
                and tok.feats.get("Tense") == "Pres"
            ):
                aux_in_c = True
                break

        if (aux_in_o and not aux_in_c) or (aux_in_c and not aux_in_o):
            return True
    return False


def remove_refl_postfix(text):
    potential_postfixes = ["ся", "сь"]

    for i in range(len(potential_postfixes)):
        position = text.rfind(potential_postfixes[i])
        if position != -1 and len(text) - position < 4:
            text = text[:position] + text[position + len(potential_postfixes[i]) :]
            break

    return text


def related_stems(first, second):
    first_stem = stemmer.stem(first)
    second_stem = stemmer.stem(second)
    return (first_stem in second_stem) or (second_stem in first_stem)


def morph(o_toks, c_toks):
    return (
        len(o_toks) == len(c_toks) == 1
        and o_toks[0].lemma != c_toks[0].lemma
        and related_stems(o_toks[0].lemma, c_toks[0].lemma)
    )


def morph_ml(o_toks, c_toks):
    return (
        ML
        and len(o_toks) == len(c_toks) == 1
        and is_morph(o_toks[0].text, c_toks[0].text)
    )


def refl(o_toks, c_toks):
    if (len(o_toks) == len(c_toks) == 1) and (o_toks[0].pos == c_toks[0].pos == "VERB"):
        o_basic = remove_refl_postfix(o_toks[0].lemma)
        c_basic = remove_refl_postfix(c_toks[0].lemma)
        if (
            (o_basic != o_toks[0].lemma and c_basic == c_toks[0].lemma)
            or (o_basic == o_toks[0].lemma and c_basic != c_toks[0].lemma)
        ) and (
            related_stems(o_basic, c_basic)
            or o_basic == c_toks[0].text
            or c_basic == o_toks[0].text
        ):
            return True
    return False


def agrnum(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    o_nums = [o_tok.feats.get("Number", None) for o_tok in o_toks]
    c_nums = [c_tok.feats.get("Number", None) for c_tok in c_toks]
    lemmas_match_flags = [
        (o_toks[i].lemma == c_toks[i].lemma) for i in range(len(o_toks))
    ]

    if (
        (len(set(o_nums)) == len(set(c_nums)) == 1)
        and (not (None in o_nums))
        and (not (None in c_nums))
        and (o_nums != c_nums)
        and (sum(lemmas_match_flags) == len(lemmas_match_flags))
    ):
        return True

    return False


def wrong_case(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    o_cases = [o_tok.feats.get("Case", None) for o_tok in o_toks]
    c_cases = [c_tok.feats.get("Case", None) for c_tok in c_toks]
    lemmas_match_flags = [
        (o_toks[i].lemma == c_toks[i].lemma) for i in range(len(o_toks))
    ]

    if (
        (len(set(o_cases)) == len(set(c_cases)) == 1)
        and (not (None in o_cases))
        and (not (None in c_cases))
        and (o_cases != c_cases)
        and (sum(lemmas_match_flags) == len(lemmas_match_flags))
    ):
        return True
    return False


def noun_case(o_toks, c_toks):
    pos_set = {tok.pos for tok in o_toks + c_toks}
    return len(pos_set & {"PROPN", "NOUN", "PRON"}) > 0


def nominative(c_toks):
    c_cases = [c_tok.feats.get("Case", None) for c_tok in c_toks]
    return "Nom" in c_cases


def agrgender(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    o_genders = [o_tok.feats.get("Gender", None) for o_tok in o_toks]
    c_genders = [c_tok.feats.get("Gender", None) for c_tok in c_toks]
    lemmas_match_flags = [
        (o_toks[i].lemma == c_toks[i].lemma) for i in range(len(o_toks))
    ]

    if (
        (len(set(o_genders)) == len(set(c_genders)) == 1)
        and (not (None in o_genders))
        and (not (None in c_genders))
        and (o_genders != c_genders)
        and (sum(lemmas_match_flags) == len(lemmas_match_flags))
    ):
        return True
    return False


def agrpers(o_toks, c_toks):
    if len(o_toks) != len(c_toks):
        return False

    o_pers = [o_tok.feats.get("Person", None) for o_tok in o_toks]
    c_pers = [c_tok.feats.get("Person", None) for c_tok in c_toks]
    lemmas_match_flags = [
        (o_toks[i].lemma == c_toks[i].lemma) for i in range(len(o_toks))
    ]

    if (
        (len(set(o_pers)) == len(set(c_pers)) == 1)
        and (not (None in o_pers))
        and (not (None in c_pers))
        and (set(o_pers) != set(c_pers))
        and (sum(lemmas_match_flags) == len(lemmas_match_flags))
    ):
        return True

    return False


def mode(o_toks, c_toks):
    aux_in_o_toks = [
        (tok.pos == "AUX" and tok.feats.get("Mood") == "Cnd") for tok in o_toks
    ]
    aux_in_c_toks = [
        (tok.pos == "AUX" and tok.feats.get("Mood") == "Cnd") for tok in c_toks
    ]

    if (any(aux_in_o_toks) and not any(aux_in_c_toks)) or (
        any(aux_in_c_toks) and not any(aux_in_o_toks)
    ):
        return True
    return False


def ref(o_toks, c_toks):
    pos_set = {tok.pos for tok in o_toks + c_toks}
    if pos_set.issubset({"DET", "PRON"}):
        return True
    return False


def conj(o_toks, c_toks):
    pos_set = {tok.pos for tok in o_toks + c_toks}
    if pos_set.issubset({"CCONJ", "SCONJ"}):
        return True
    return False


def com(o_toks, c_toks):
    o_cmp_flags = [
        True if tok.feats.get("Degree") == "Cmp" else False for tok in o_toks
    ]
    c_cmp_flags = [
        True if tok.feats.get("Degree") == "Cmp" else False for tok in c_toks
    ]
    if any(o_cmp_flags + c_cmp_flags):
        return True
    else:
        return False


def impers(o_toks, c_toks):
    o_rel = {tok.rel for tok in o_toks}
    c_rel = {tok.rel for tok in c_toks}
    if (
        ("nsubj" in o_rel and "nsubj" not in c_rel)
        or ("nsubj" in c_rel and "nsubj" not in o_rel)
    ) and ((len(o_toks) > 1) and (len(c_toks) > 1)):
        return True
    return False


def cs(o_toks, c_toks):
    for tok in o_toks:
        if tok.feats.get("Foreign") == "Yes":
            return True
    return False


def lex(o_toks, c_toks):
    if (
        len(o_toks) == len(c_toks) == 1
        and pymorphy_parser.word_is_known(o_toks[0].text)
        and o_toks[0].lemma != c_toks[0].lemma
    ):
        return True
    return False


def prep(o_toks, c_toks):
    pos_set = {tok.pos for tok in c_toks}
    if pos_set.issubset({"ADP"}):
        return True
    return False


def ortho(o_toks, c_toks):
    if (len(o_toks) == len(c_toks) == 1) and (
        lev(o_toks[0].text, c_toks[0].text) >= 0.8
    ):
        return True
    return False


def aux(o_toks, c_toks):
    o_aux_flags = [(tok.lemma == "быть" or tok.lemma == "стать") for tok in o_toks]
    c_aux_flags = [(tok.lemma == "быть" or tok.lemma == "стать") for tok in c_toks]
    if (
        (len(o_toks) > 1)
        and (len(c_toks) > 1)
        and ((sum(o_aux_flags)) != (sum(c_aux_flags)))
    ):
        return True
    return False


def syntax(o_toks, c_toks):
    if len(o_toks) > 1 or len(c_toks) > 1:
        return True
    return False


def word_order(o_toks, c_toks):
    o_set = sorted([o.text.lower() for o in o_toks])
    c_set = sorted([c.text.lower() for c in c_toks])
    if o_set == c_set and len(o_set) > 1:
        return True
    return False
