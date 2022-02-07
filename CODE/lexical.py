import copy
from enum import Enum
import re

from exceptions import LexicalError, IndentError


class Type(Enum):
	Identifier = 0
	Keyword = 1
	Operator = 2
	Divider = 3
	Number = 4
	String = 5
	
	ERROR = -1


class Token:
	content: str = ""
	line: int = 0
	pos: int = 0
	
	def __init__(self, line: int, pos: int, content: str = ""):
		self.line = line
		self.pos = pos
		self.content = content
	
	def __str__(self):
		return """Token:
        token_type = {}
        content = {}
        line = {}
        position = {}""".format(
			self.type(),
			self.content,
			self.line,
			self.pos)
	
	def __len__(self) -> int:
		return len(self.content)
	
	def as_symbol(self):
		if self.is_terminal():
			return "<" + str(self.type())[5:] + ">"
		else:
			return self.content
	
	def is_terminal(self):
		return True
	
	def type(self):
		return Type.ERROR
	
	def copy(self):
		return copy.deepcopy(self)


class TokenIdentifier(Token):
	def type(self):
		return Type.Identifier


class TokenKeyword(Token):
	def type(self):
		return Type.Keyword
	
	def is_terminal(self):
		return False


class TokenOperator(Token):
	def type(self):
		return Type.Operator
	
	def is_terminal(self):
		return False


class TokenDivider(Token):
	def type(self):
		return Type.Divider
	
	def is_terminal(self):
		return False


class TokenIndent(TokenDivider):
	def __init__(self, indent: bool, line: int, pos: int):
		super().__init__(line, pos, "indent" if indent else "dedent")


class TokenNumber(Token):
	def type(self):
		return Type.Number


class TokenString(Token):
	def type(self):
		return Type.String


class Pattern:
	def token(self, match: str, line: int, pos: int):
		return Token(line, pos, match)
	
	def regex(self):
		return ""


class PatternNumber(Pattern):
	def regex(self):
		return r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)"
	
	def token(self, match: str, line: int, pos: int):
		return TokenNumber(line, pos, match)


class PatternDivider(Pattern):
	def regex(self):
		return r"(?:,|\(|\)|\[|\]|{|}|:)"
	
	def token(self, match: str, line: int, pos: int):
		return TokenDivider(line, pos, match)


class PatternOperator(Pattern):
	def regex(self):
		return r"(?:\+|\-|\*{1,2}|\/|\%|={1,2}|!=|<=|>=|<|>|\bnot\b|\band\b|\bor\b|\bin\b)"
	
	def token(self, match: str, line: int, pos: int):
		return TokenOperator(line, pos, match)


class PatternKeyword(Pattern):
	def regex(self):
		return r"(?:\bdef\b|\breturn\b|\bbreak\b|\bcontinue\b|\bpass\b|\bfor\b|\bwhile\b|\bif\b|\belif\b|\belse\b|\bprint\b|\brange\b|\blen\b|\bin\b|\bdict\b|\bTrue\b|\bFalse\b)"
	
	def token(self, match: str, line: int, pos: int):
		return TokenKeyword(line, pos, match)


class PatternString(Pattern):
	def regex(self):
		return r"(?:\".*\"|\'.*\')"
	
	def token(self, match: str, line: int, pos: int):
		return TokenString(line, pos, match)


class PatternIdentifier(Pattern):
	def regex(self):
		return r"[A-Za-z_][A-Za-z_0-9]*"
	
	def token(self, match: str, line: int, pos: int):
		return TokenIdentifier(line, pos, match)


class LexicalAnalyzer:
	patterns = [PatternKeyword(), PatternOperator(), PatternIdentifier(), PatternNumber(), PatternDivider(), PatternString()]
	
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
			
			if suc:
				continue
			
			res = re.match("\n", code)
			if res is not None:
				code = code[1:]
				tokens.append(TokenDivider(line, pos, "newline"))
				pos = 0
				line += 1
				
				res = re.search("^ +", code)
				if res is not None:
					raise IndentError(line + 1)
				
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
				
				continue
			
			res = re.search("^ +", code)
			if res is not None:
				endpos = res.regs[0][1]
				pos += endpos
				code = code[endpos:]
			else:
				raise LexicalError(pos, line, code_copy)
		
		return tokens