from .alignment import Alignment
from .text_processor import TextProcessor
from .merger import get_rule_edits
from .classifier import classify


class Annotator:
    """Main class for the tool. Combines other classes into easy-to-use pipelines"""

    def __init__(self):
        self.processor = TextProcessor()

    def process(self, text):
        """Preprocesses text and adds additional metadata to it"""
        return self.processor.process(text)

    def align(self, orig, corr):
        """Aligns single-token edits"""
        orig = self.process(orig)
        corr = self.process(corr)
        return Alignment(orig, corr), orig, corr

    def merge(self, alignment, algorithm="rules"):
        """Merges extracted single-token edits based on an algorithm specified.
        Can use following algorithms: rules, all-split, all-merge, all-equal"""
        if algorithm == "rules":
            # Merge based on a set of strict rules
            edits = get_rule_edits(alignment)
        elif algorithm == "all-split":
            # Do not merge any edits
            edits = alignment.get_all_split_edits()
        elif algorithm == "all-merge":
            # Merge all consecutive edits
            edits = alignment.get_all_merge_edits()
        elif algorithm == "all-equal":
            # Merge all consecutive edits of the same POS
            edits = alignment.get_all_equal_edits()
        else:
            raise Exception(
                "Unknown merging algorithm. Choose from: "
                "rules, all-split, all-merge, all-equal."
            )
        return edits

    def classify(self, edit):
        """Assigns a class to a passed edit object"""
        return classify(edit)

    def annotate(self, orig, cor, merging="rules"):
        """
        Main pipeline for annotation. Accepts two versions of the text: original and corrected.
        Returns a list of edit objects with information about each extracted edit.
        """
        alignment, orig_tokenized, cor_tokenized = self.align(orig, cor)
        edits = self.merge(alignment, merging)
        for edit in edits:
            edit = self.classify(edit)
        return edits, orig_tokenized, cor_tokenized
