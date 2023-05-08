""" Module implementing merging rules. """


from .edit import Edit
from itertools import combinations, groupby
from re import sub
import Levenshtein
from string import punctuation

open_pos = {"ADJ", "AUX", "ADV", "NOUN", "VERB"}


def get_rule_edits(alignment):
    """Merges edits based on a set of rules"""
    edits = []
    for op, group in groupby(
        alignment.align_seq, lambda x: x[0][0] if x[0][0] in {"M", "T"} else False
    ):
        group = list(group)
        if op == "M":
            continue
        elif op == "T":
            for seq in group:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
        else:
            processed = process_seq(group, alignment)
            for seq in processed:
                edits.append(Edit(alignment.orig, alignment.cor, seq[1:]))
    return edits


def process_seq(seq, alignment):
    """Processes a given sequence for merging based on rules"""
    if len(seq) <= 1:
        return seq
    ops = [op[0] for op in seq]
    if set(ops) == {"D"} or set(ops) == {"I"}:
        return merge_edits(seq)

    content = False
    # We loop through all possible combinations of tokens in the sequence, starting from the largest
    combos = list(combinations(range(0, len(seq)), 2))
    combos.sort(key=lambda x: x[1] - x[0], reverse=True)
    for start, end in combos:
        # Only consider sequences that have substitutions in them
        if "S" not in ops[start : end + 1]:
            continue
        o = alignment.orig[seq[start][1] : seq[end][2]]
        c = alignment.cor[seq[start][3] : seq[end][4]]
        if o[-1].text.lower() == c[-1].text.lower():
            if start == 0 and (
                (len(o) == 1 and c[0].text[0].isupper())
                or (len(c) == 1 and o[0].text[0].isupper())
            ):
                return merge_edits(seq[start : end + 1]) + process_seq(
                    seq[end + 1 :], alignment
                )
            if (len(o) > 1 and is_punct(o[-2])) or (len(c) > 1 and is_punct(c[-2])):
                return (
                    process_seq(seq[: end - 1], alignment)
                    + merge_edits(seq[end - 1 : end + 1])
                    + process_seq(seq[end + 1 :], alignment)
                )

        o_str = "".join([tok.text.lower() for tok in o])
        s = sub("['-]", "", o_str)
        c_str = "".join([tok.text.lower() for tok in c])
        t = sub("['-]", "", c_str)
        if s == t or (
            len(o) + len(c) <= 4
            and "-" in o_str + c_str
            and Levenshtein.ratio(s, t) >= 0.75
        ):
            return (
                process_seq(seq[:start], alignment)
                + merge_edits(seq[start : end + 1])
                + process_seq(seq[end + 1 :], alignment)
            )

        pos_set = set([tok.pos for tok in o] + [tok.pos for tok in c])
        if len(o) != len(c) and (
            len(pos_set) == 1 or pos_set.issubset({"AUX", "PART", "VERB"})
        ):
            return (
                process_seq(seq[:start], alignment)
                + merge_edits(seq[start : end + 1])
                + process_seq(seq[end + 1 :], alignment)
            )

        o_numcases = [(tok.feats.get("Number"), tok.feats.get("Case")) for tok in o]
        c_numcases = [(tok.feats.get("Number"), tok.feats.get("Case")) for tok in c]
        if len(set(o_numcases)) == 1 and len(set(c_numcases)) == 1:
            return (
                process_seq(seq[:start], alignment)
                + merge_edits(seq[start : end + 1])
                + process_seq(seq[end + 1 :], alignment)
            )

        if end - start < 2:
            if len(o) == len(c) == 2:
                return process_seq(seq[: start + 1], alignment) + process_seq(
                    seq[start + 1 :], alignment
                )
            if (ops[start] == "S" and char_cost(o[0], c[0]) > 0.75) or (
                ops[end] == "S" and char_cost(o[-1], c[-1]) > 0.75
            ):
                return process_seq(seq[: start + 1], alignment) + process_seq(
                    seq[start + 1 :], alignment
                )
        if not pos_set.isdisjoint(open_pos):
            content = True
    if content:
        return merge_edits(seq)
    else:
        return seq


def is_punct(token):
    return token.pos == "PUNCT" or token.text in punctuation


def char_cost(a, b):
    return Levenshtein.ratio(a.text, b.text)


def merge_edits(seq):
    if seq:
        return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
    else:
        return seq
