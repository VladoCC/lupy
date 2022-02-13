class AnalyzerError(Exception):
    pass


class LexicalError(AnalyzerError):
    def __init__(self, pos, line, code):
        err_line = code.split('\n')[line]
        incorrect_line = f"Incorrect code in position {pos + 1} line {line + 1}: "
        self.message = "Lexical Error\n" + incorrect_line + err_line + "\n" + " " * len(incorrect_line) + " " * pos + "↑"
        super().__init__(self.message)


class IndentError(AnalyzerError):
    def __init__(self, line):
        super().__init__(f"Lexical Error\nUnexpected spaces at the start of the line {line}")


class SemanticError(AnalyzerError):
    def __init__(self, *args):
        super(SemanticError, self).__init__(*args)


class SyntacticError(AnalyzerError):
    def __init__(self):
        super().__init__("Syntactic Error\nUnable to parse code using Earley Parser")


class NoNewLineError(AnalyzerError):
    def __init__(self):
        super().__init__("Syntactic Error\nNo new line at end of file")
