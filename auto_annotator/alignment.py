""" Main class for aligning single tokens between original and corrected versions of the text """

import Levenshtein
from itertools import groupby

from .edit import Edit


class Alignment:
    def __init__(self, orig, cor):
        self.orig = orig.tokens
        self.cor = cor.tokens
        self.cost_matrix, self.op_matrix = self.align()
        self.align_seq = self.get_cheapest_align_seq()

    def align(self):
        """Builds a cost and operation matrices to be used later in the alignment algorithm"""

        o_len = len(self.orig)
        c_len = len(self.cor)
        o_low = [o.text.lower() for o in self.orig]
        c_low = [c.text.lower() for c in self.cor]

        # Cost matrix contains the costs of operations between tokens in the original and corrected texts
        cost_matrix = [[0.0 for j in range(c_len + 1)] for i in range(o_len + 1)]
        # Operation matrix contains the selected operations between pairs of token in the original and corrected texts
        op_matrix = [["O" for j in range(c_len + 1)] for i in range(o_len + 1)]

        # Initialize the matrices by setting the 0th row and 0th column
        for i in range(1, o_len + 1):
            cost_matrix[i][0] = cost_matrix[i - 1][0] + 1
            op_matrix[i][0] = "D"
        for j in range(1, c_len + 1):
            cost_matrix[0][j] = cost_matrix[0][j - 1] + 1
            op_matrix[0][j] = "I"

        # Loop through the matrix, selecting optimal operations between every pair of tokens
        for i in range(o_len):
            for j in range(c_len):
                if self.orig[i].text == self.cor[j].text:
                    cost_matrix[i + 1][j + 1] = cost_matrix[i][j]
                    op_matrix[i + 1][j + 1] = "M"
                else:
                    # Calculate costs of every operation
                    del_cost = cost_matrix[i][j + 1] + 1
                    ins_cost = cost_matrix[i + 1][j] + 1
                    trans_cost = float("inf")
                    sub_cost = cost_matrix[i][j] + self.get_sub_cost(
                        self.orig[i], self.cor[j]
                    )

                    # Transposition cost calculation
                    k = 1
                    while (
                        i - k >= 0
                        and j - k >= 0
                        and cost_matrix[i - k + 1][j - k + 1]
                        != cost_matrix[i - k][j - k]
                    ):
                        if sorted(o_low[i - k : i + 1]) == sorted(c_low[j - k : j + 1]):
                            trans_cost = cost_matrix[i - k][j - k] + k
                            break
                        k += 1

                    # Select the operation with the cheapest cost
                    costs = [trans_cost, sub_cost, ins_cost, del_cost]
                    l = costs.index(min(costs))
                    cost_matrix[i + 1][j + 1] = costs[l]
                    if l == 0:
                        op_matrix[i + 1][j + 1] = "T" + str(k + 1)
                    elif l == 1:
                        op_matrix[i + 1][j + 1] = "S"
                    elif l == 2:
                        op_matrix[i + 1][j + 1] = "I"
                    else:
                        op_matrix[i + 1][j + 1] = "D"
        return cost_matrix, op_matrix

    def get_sub_cost(self, o, c):
        """Calculate the cost of a substitution operation using the Levenshtein distance with additional penalties"""
        if o.text.lower() == c.text.lower():
            return 0
        if o.lemma == c.lemma:
            lemma_cost = 0
        else:
            lemma_cost = 0.499
        if o.pos == c.pos:
            pos_cost = 0
        else:
            pos_cost = 0.5
        char_cost = 1 - Levenshtein.ratio(o.text, c.text)
        return lemma_cost + pos_cost + char_cost

    def get_cheapest_align_seq(self):
        """Align the tokens by selecting the optimal operation in the cost matrix"""
        i = len(self.op_matrix) - 1
        j = len(self.op_matrix[0]) - 1
        align_seq = []
        while i + j != 0:
            op = self.op_matrix[i][j]
            if op in {"M", "S"}:
                align_seq.append((op, i - 1, i, j - 1, j))
                i -= 1
                j -= 1
            elif op == "D":
                align_seq.append((op, i - 1, i, j, j))
                i -= 1
            elif op == "I":
                align_seq.append((op, i, i, j - 1, j))
                j -= 1
            else:
                k = int(op[1:])
                align_seq.append((op, i - k, i, j - k, j))
                i -= k
                j -= k
        align_seq.reverse()
        return align_seq

    def get_all_split_edits(self):
        """all-split merge algorithm. i.e. don't merge any edits"""
        edits = []
        for align in self.align_seq:
            if align[0] != "M":
                edits.append(Edit(self.orig, self.cor, align[1:]))
        return edits

    def get_all_merge_edits(self):
        """all-merge merge algorithm. i.e. merge all edits"""
        edits = []
        for op, group in groupby(
            self.align_seq, lambda x: True if x[0] == "M" else False
        ):
            if not op:
                merged = self.merge_edits(list(group))
                edits.append(Edit(self.orig, self.cor, merged[0][1:]))
        return edits

    def get_all_equal_edits(self):
        """all-equal merge algorithm. i.e. merge all edits of the same POS"""
        edits = []
        for op, group in groupby(self.align_seq, lambda x: x[0]):
            if op != "M":
                merged = self.merge_edits(list(group))
                edits.append(Edit(self.orig, self.cor, merged[0][1:]))
        return edits

    def merge_edits(self, seq):
        if seq:
            return [("X", seq[0][1], seq[-1][2], seq[0][3], seq[-1][4])]
        else:
            return seq

    def __str__(self):
        orig = " ".join(["Orig:"] + [tok.text for tok in self.orig])
        cor = " ".join(["Cor:"] + [tok.text for tok in self.cor])
        cost_matrix = "\n".join(
            ["Cost Matrix:"] + [str(row) for row in self.cost_matrix]
        )
        op_matrix = "\n".join(
            ["Operation Matrix:"] + [str(row) for row in self.op_matrix]
        )
        seq = "Best alignment: " + str([a[0] for a in self.align_seq])
        return "\n".join([orig, cor, cost_matrix, op_matrix, seq])
