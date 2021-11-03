from enum import Enum, auto

from typing import List

from lexical import Token, Type


class Construction(Enum):
	Condition = auto()
	Else = auto()
	Loop = auto()
	Function = auto()


def generate(tokens):
	lua_code = ""
	line = 0
	pos = 0

	indent_state = None
	indent_level = 0
	oneliner = False

	while len(tokens) > 0:
		token = tokens[0]
		assert isinstance(token, Token)
		while token.line > line:
			line += 1
			pos = 0
			lua_code += "\n"
		while token.pos > pos:
			pos += 1
			lua_code += " "

		if token.type() == Type.Identifier or token.type() == Type.String \
			or token.type() == Type.Number:
			lua_code += token.content
			pos += len(token.content)
		elif token.type() == Type.Operator:
			if token.content == "**":
				lua_op = "^"
			elif token.content == "!=":
				lua_op = "~="
			else:
				lua_op = token.content
			lua_code += lua_op
			pos += len(token.content)
		elif token.type() == Type.Divider:
			whitelist = ["(", ")", ","]
			if token.content in whitelist:
				lua_code += token.content
				pos += len(token.content)
			elif token.content == ":":
				if indent_state == Construction.Condition:
					lua_code += " then"
				elif indent_state == Construction.Loop:
					lua_code += " do"
				
				if tokens[1].content != "newline":
					oneliner = True

				if indent_state is not None:
					pos += 1

			elif token.content == "dedent":
				if indent_state != Construction.Condition:
					while indent_level > pos:
						pos += 1
						lua_code += " "
					lua_code += "end\n"
				pos += len(token.content)
				indent_state = None
				indent_level = 0
			elif token.content == "{" or token.content == "[":
				dict_tokens = [token]
				while not tokens[1].content == "}" and not tokens[1].content == "]":
					dict_tokens.append(tokens.pop(1))
				dict_tokens.append(tokens.pop(1))
				last = dict_tokens[len(dict_tokens) - 1]
				lua_code += generate_table(dict_tokens)
				line = last.line
				pos = last.pos + len(last.content)
			elif token.content == "newline" and oneliner:
				oneliner = False
				lua_code += " end"
		elif token.type() == Type.Keyword:
			whitelist = ["return", "break", "continue", "print"]
			constitutions = {"True": "true", "False": "false", "Node": "nil"}
			if token.content in whitelist:
				lua_code += token.content
				pos += len(token.content)
			elif token.content in constitutions.keys():
				lua_code += constitutions[token.content]
				pos += len(token.content)
			elif token.content == "len":
				pos += len(token.content) + 2
				lua_code += "#"
				tokens.pop(1)
				tokens.pop(3)
			elif token.content == "def":
				pos += len(token.content)
				lua_code += "function"
				indent_state = Construction.Function
			elif token.content == "if" or token.content == "elif":
				pos += len(token.content)
				if token.content == "elif":
					lua_code += "else"
				lua_code += "if"
				indent_state = Construction.Condition
				indent_level = token.pos
			elif token.content == "else":
				pos += len(token.content)
				lua_code += token.content
				indent_state = Construction.Else
				indent_level = token.pos
			elif token.content == "while" or token.content == "for":
				pos += len(token.content)
				lua_code += token.content
				indent_state = Construction.Loop
				indent_level = token.pos
			elif token.content == "in":
				for_tokens = []
				while tokens[1].content != ":":
					for_tokens.append(tokens.pop(1))
				
				last = for_tokens[len(for_tokens) - 1]
				
				if for_tokens[0].content == "range":
					lua_code += "= "
					for_tokens.pop(0)
					for_tokens.pop(0)
					last = for_tokens.pop(len(for_tokens) - 1)
					for_tokens = as_proxy_list(for_tokens)
					first_end = -1
					depth = 0
					for i in range(len(for_tokens)):
						t = for_tokens[i]
						if t.content == "(":
							depth += 1
						elif t.content == ")":
							depth -= 1
						elif t.content == "," and depth == 0:
							first_end = i
							break

					if first_end == -1:
						lua_code += "0, "
					
					lua_code += generate(for_tokens)
					lua_code += " - 1"
				else:
					lua_code += token.content
					lua_code += " pairs("
					lua_code += generate(as_proxy_list(for_tokens))
					lua_code += ")"
				line = last.line
				pos = last.pos + len(last.content)
			elif token.content == "dict":
				pos += len(token.content)
				dict_tokens = []
				active = True
				counter = 0
				while active:
					if tokens[1].content == "(":
						counter += 1
					elif tokens[1].content == ")":
						counter -= 1
					active = counter != 0
					dict_tokens.append(tokens.pop(1))
				last = dict_tokens[len(dict_tokens) - 1]
				lua_code += generate_table(dict_tokens)
				line = last.line
				pos = last.pos + len(last.content)
		else:
			lua_code += token.content
			pos += len(token.content)
		tokens.pop(0)

	return lua_code


def generate_table(dict_tokens: List[Token]):
	if len(dict_tokens) == 2:
		return "{}"
	start = dict_tokens.pop(0)
	dict_tokens.pop(len(dict_tokens) - 1)
	line = start.line
	code = "{"
	pos = start.pos + 1
	delimiter = ":" if any(token.content == ":" for token in dict_tokens) else "="
	if delimiter == ":":
		code += "["

	add_bracket = False
	while len(dict_tokens) > 0:
		token = dict_tokens[0]
		assert isinstance(token, Token)
		while token.line > line:
			line += 1
			pos = 0
			code += "\n"
		while token.pos > pos:
			pos += 1
			code += " "

		if add_bracket:
			add_bracket = False
			code += "["
		if delimiter == ":" and token.content == ":":
			code += "] ="
		elif token.content == "=":
			code += " = "
		else:
			code += generate([ProxyToken(token)])
		pos += len(token.content)
		if delimiter == ":" and token.content == ",":
			add_bracket = True
		dict_tokens.pop(0)
	code += "}"
	return code


def as_proxy_list(tokens):
	proxy_tokens = []
	first = tokens[0]
	for token in tokens:
		proxy_line = token.line - first.line
		proxy_pos = token.pos - first.pos
		proxy_tokens.append(ProxyToken(token, proxy_line, proxy_pos))
	return proxy_tokens


class ProxyToken(Token):
	def __init__(self, token: Token, line: int = 0, pos: int = 0):
		super().__init__(line, pos, token.content)
		self.token_type = token.type()

	def type(self):
		return self.token_type
