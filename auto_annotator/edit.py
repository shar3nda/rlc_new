class Edit:
    """Main class for a single edit object"""

    def __init__(self, orig, cor, edit, err_type="NA"):
        self.o_start = edit[0]
        self.o_end = edit[1]
        self.o_toks = orig[self.o_start : self.o_end]
        self.o_str = " ".join(map(lambda x: x.text, self.o_toks)) if self.o_toks else ""
        self.c_start = edit[2]
        self.c_end = edit[3]
        self.c_toks = cor[self.c_start : self.c_end]
        self.c_str = " ".join(map(lambda x: x.text, self.c_toks)) if self.c_toks else ""
        self.type = err_type

    def minimise(self):
        """Removes matching tokens from the edit"""
        while (
            self.o_toks and self.c_toks and self.o_toks[0].text == self.c_toks[0].text
        ):
            self.o_toks = self.o_toks[1:]
            self.c_toks = self.c_toks[1:]
            self.o_start += 1
            self.c_start += 1
        while (
            self.o_toks and self.c_toks and self.o_toks[-1].text == self.c_toks[-1].text
        ):
            self.o_toks = self.o_toks[:-1]
            self.c_toks = self.c_toks[:-1]
            self.o_end -= 1
            self.c_end -= 1
        self.o_str = self.o_toks.text if self.o_toks else ""
        self.c_str = self.c_toks.text if self.c_toks else ""
        return self

    def __str__(self):
        orig = "Orig: " + str([self.o_start, self.o_end, self.o_str])
        cor = "Cor: " + str([self.c_start, self.c_end, self.c_str])
        type = "Type: " + repr(self.type)
        return ", ".join([orig, cor, type])
