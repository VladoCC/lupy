from enum import Enum
import re


class Type(Enum):
    Identifier = 0
    Keyword = 1
    Operator = 2
    Divider = 3
    Number = 4
    String = 5

    ERROR = -1


class Token:
    token_type = Type.Identifier
    content = ""
    line = 0
    pos = 0

    def __init__(self, line: int, pos: int, content: str = ""):
        self.line = line
        self.pos = pos
        self.token_type = self.type()
        self.content = content

    def __str__(self):
        return """Token:
        token_type = {}
        content = {}
        line = {}
        position = {}""".format(
            self.token_type,
            self.content,
            self.line,
            self.pos)

    def as_symbol(self):
        return "<" + str(self.token_type)[5:] + ">"

    def type(self):
        return Type.ERROR


class NonTerminalToken(Token):
    def as_symbol(self):
        return self.content


class TokenIdentifier(Token):
    def type(self):
        return Type.Identifier


class TokenKeyword(NonTerminalToken):
    def type(self):
        return Type.Keyword


class TokenOperator(NonTerminalToken):
    def type(self):
        return Type.Operator


class TokenDivider(NonTerminalToken):
    def __init__(self, line: int, pos: int, content: str):
        super().__init__(line, pos, content)

    def type(self):
        return Type.Divider


class TokenIndent(TokenDivider):
    def __init__(self, indent: bool, line: int, pos: int):
        super().__init__(line, pos, "indent" if indent else "dedent")


class TokenNumber(Token):
    def type(self):
        return Type.Number


class TokenString(Token):
    def type(self):
        return Type.String


class AbstractPattern:
    def __init__(self):
        pass

    def token(self, match: str, line: int, pos: int):
        return Token(line, pos, match)

    def regex(self):
        return ""


class PatternNumber(AbstractPattern):
    def regex(self):
        return r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)"

    def token(self, match: str, line: int, pos: int):
        return TokenNumber(line, pos, match)


class PatternDivider(AbstractPattern):
    def regex(self):
        return r"(?:,|\(|\)|\[|\]|{|}|:)"

    def token(self, match: str, line: int, pos: int):
        return TokenDivider(line, pos, match)


class PatternOperator(AbstractPattern):
    def regex(self):
        return r"(?:\+|\-|\*{1,2}|\/|\%|={1,2}|!=|<|>|<=|>=|\bnot\b|\band\b|\bor\b|\bin\b)"

    def token(self, match: str, line: int, pos: int):
        return TokenOperator(line, pos, match)


class PatternKeyword(AbstractPattern):
    def regex(self):
        return r"(?:\bdef\b|\breturn\b|\bbreak\b|\bcontinue\b|\bpass\b|\bfor\b|\bwhile\b|\bif\b|\belif\b|\belse\b|\bprint\b|\brange\b|\blen\b|\bin\b|\bdict\b|\bTrue\b|\bFalse\b|\bNone\b)"

    def token(self, match: str, line: int, pos: int):
        return TokenKeyword(line, pos, match)


class PatternString(AbstractPattern):
    def regex(self):
        return r"(?:\".*\"|\'.*\')"

    def token(self, match: str, line: int, pos: int):
        return TokenString(line, pos, match)


class PatternIdentifier(AbstractPattern):
    def regex(self):
        return r"[A-Za-z_][A-Za-z_0-9]*"

    def token(self, match: str, line: int, pos: int):
        return TokenIdentifier(line, pos, match)


class LexicalError(Exception):
    def __init__(self, pos, line, code):
        err_line = code.split('\n')[line]
        incorrect_line = f"Incorrect code in position {pos + 1} line {line + 1}: "
        self.message = "\n" + incorrect_line + err_line + "\n" + " " * len(incorrect_line) + " " * pos + "↑"
        super().__init__(self.message)


class LexicalAnalyzer:
    patterns = [PatternKeyword(), PatternIdentifier(), PatternNumber(), PatternDivider(), PatternOperator(), PatternString()]

    def parse(self, code):
        code_copy = code
        tokens = []
        pos = 0
        line = 0
        indent_level = 0
        while len(code) > 0:
            suc = False
            for pattern in self.patterns:
                regex = pattern.regex()
                res = re.search("^" + regex, code)
                if res is not None:
                    endpos = res.regs[0][1]
                    token = pattern.token(code[0:endpos], line, pos)
                    code = code[endpos:]
                    suc = True
                    tokens.append(token)
                    pos += endpos
                    break

            if not suc:
                res = re.match("\n", code)
                if res is not None:
                    code = code[1:]
                    tokens.append(TokenDivider(line, pos, 'newline'))
                    pos = 0
                    line += 1

                    res = re.search("^\t+", code)
                    if res is not None:
                        endpos = res.regs[0][1]
                    else:
                        endpos = 0

                    pos += 4 * endpos  # standard python tab size

                    for i in range(abs(endpos - indent_level)):
                        tokens.append(TokenIndent(endpos > indent_level, line, pos))
                    indent_level = endpos
                    code = code[endpos:]

                    suc = True

            if not suc:
                res = re.search("^ +", code)
                if res is not None:
                    endpos = res.regs[0][1]
                    pos += endpos
                    code = code[endpos:]
                    suc = True

            if not suc:
                raise LexicalError(pos, line, code_copy)

        return tokens
