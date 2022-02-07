from enum import Enum, auto
from typing import List

from syntactic import TreeToken
from lexical import Token, Type
from nltk.tree import ParentedTree


class Construction(Enum):
	Condition = auto()
	Else = auto()
	Loop = auto()
	Function = auto()


class Structure(Enum):
	If = auto()
	Else = auto()
	Loop = auto()
	Function = auto()


class State:
	def __init__(self, structure: Structure, indent_level=0, oneliner: bool = False):
		super().__init__()
		self.structure = structure
		self.oneliner = oneliner
		self.indent_level = indent_level


class Program:
	line: int = 0
	pos: int = 0
	stack: List[State] = []
	
	def __init__(self, tokens: list):
		super().__init__()
		self.tokens = tokens
	
	def next(self):
		self.tokens.pop(0)
	
	def move_to(self, pos=-1, line=-1):
		if line == -1:
			line = self.line
		
		if pos == -1:
			pos = self.pos
		
		self.line = line
		self.pos = pos
	
	def token(self):
		return self.tokens[0]
	
	def push_state(self, state: State):
		self.stack.append(state)
	
	def pop_state(self) -> State:
		return self.stack.pop()
		
		
class Generator:
	
	def __init__(self):
		self.pos = 0
		self.line = 0
		self.lua_code = ""
	
	def generate(self, tree: ParentedTree):
		self.pos = 0
		self.line = 0
		self.lua_code = ""
		self.generate_program(tree[0])
		return self.lua_code
	
	def generate_program(self, tree: ParentedTree):
		for child in tree:
			if child.label() == "<function>":
				self.generate_function(child)
			elif child.label() == "<sentence>":
				self.generate_sentence(child)
			elif child.label() == "<program>":
				self.generate_program(child)
			else:
				raise Exception()
		print(self.lua_code)
		
	def generate_function(self, tree: ParentedTree):
		start_token: Token = tree[0].token
		self.go_to_pos(start_token.pos, start_token.line)
		self.add("function ", 4)
		self.generate_terminal(tree[1])
		self.add("(")
		if isinstance(tree[3], ParentedTree):
			self.generate_identifiers(tree[3])
		self.add(")")
		colon: Token = tree[-2].token
		self.go_to_pos(colon.pos + 1, colon.line)
		block = tree[-1]
		self.generate_block(block)
		if len(block) == 1:
			self.add(" end", 0)
		else:
			self.add("\n" + " " * start_token.pos + "end", 0)
	
	def generate_block(self, tree: ParentedTree):
		if len(tree) == 1:
			self.generate_simple_sentence(tree[0])
		else:
			self.newline()
			self.generate_sentences(tree[2])
			
	def generate_sentences(self, tree: ParentedTree):
		current = tree[0]
		self.generate_sentence(current)
		if len(tree) > 1:
			self.generate_sentences(tree[1])
	
	def generate_sentence(self, tree: ParentedTree):
		internal = tree[0]
		if internal.label() == "<simple_sentence>":
			self.generate_simple_sentence(internal)
		elif internal.label() == "<complex_sentence>":
			self.generate_complex_sentence(internal)
	
	def generate_complex_sentence(self, tree: ParentedTree):
		internal = tree[0]
		if internal.label() == "<condition>":
			self.generate_condition(internal)
		elif internal.label() == "<loop>":
			self.generate_loop(internal)
	
	def generate_condition(self, tree: ParentedTree):
		if_token: Token = tree[0].token
		self.go_to_pos(if_token.pos, if_token.line)
		self.add(if_token.content)
		cond = tree[1]
		self.generate_conditional(cond)
		
		has_else = len(cond) > 3
		multiline_block = len(cond[2]) > 1
		if has_else or multiline_block:
			self.add("\n" + " " * if_token.pos + "end", 0)
		else:
			self.add(" end", 0)
			
	def generate_conditional(self, tree: ParentedTree):
		self.generate_boolean_expression(tree[0])
		colon: Token = tree[1].token
		self.go_to_pos(colon.pos, colon.line)
		self.add(" then", 1)
		self.generate_block(tree[2])
		
		if len(tree) > 3:
			self.generate_otherwise(tree[3])
		
	def generate_otherwise(self, tree: ParentedTree):
		first_token: Token = tree[0].token
		self.go_to_pos(first_token.pos, first_token.line)
		if len(tree) == 2:
			self.add("elseif", 4)
			self.generate_conditional(tree[1])
		else:
			self.add(first_token.content)
			colon: Token = tree[1].token
			self.go_to_pos(colon.pos + 1, colon.line)
			self.generate_block(tree[2])
	
	def generate_loop(self, tree: ParentedTree):
		internal = tree[0]
		if internal.label() == "<while_loop>":
			self.generate_while(internal)
		elif internal.label() == "<for_loop>":
			self.generate_for(internal)
		
		block = internal[-1]
		start_token = tree.leaves()[0].token
		if len(block) == 1:
			self.add(" end", 0)
		else:
			self.add("\n" + " " * start_token.pos + "end", 0)
	
	def generate_while(self, tree: ParentedTree):
		while_token: Token = tree[0].token
		self.go_to_pos(while_token.pos, while_token.line)
		self.add(while_token.content)
		self.generate_boolean_expression(tree[1])
		colon: Token = tree[2].token
		self.go_to_pos(colon.pos + 1, colon.line)
		self.generate_block(tree[3])
	
	def generate_for(self, tree: ParentedTree):
		for_token: Token = tree[0].token
		self.go_to_pos(for_token.pos, for_token.line)
		self.add(for_token.content)
		self.generate_terminal(tree[1])
		in_token: Token = tree[2].token
		self.go_to_pos(in_token.pos, in_token.line)
		is_collection = isinstance(tree[3], ParentedTree)
		if is_collection:
			self.add(in_token.content)
			first: Token = tree[3].leaves()[0].token
			self.go_to_pos(first.pos, first.line)
			self.add("pairs(", 0)
			self.generate_collection(tree[3])
			self.add(")", 0)
		else:
			self.add("=", 2)
			range: Token = tree[3].token
			self.go_to_pos(range.pos, range.line)
			self.pos += len(range.content)
			bracket: Token = tree[4].token
			self.go_to_pos(bracket.pos, bracket.line)
			self.pos += len(bracket.content)
			
			has_both = tree[6].token.content == ","
			end: ParentedTree = tree[5]
			if has_both:
				self.generate_mathematical_expressions(tree[5])
				self.generate_token(tree[6])
				end = tree[7]
			else:
				self.add("0, ", 0)
			
			first: Token = end.leaves()[0].token
			self.go_to_pos(first.pos, first.line)
			if len(end.leaves()) == 1:
				self.add(str(int(first.content) - 1), len(first.content))
			else:
				self.add("(", 0)
				self.generate_mathematical_expressions(end)
				self.add(" - 1)", 0)
			
			bracket: Token = tree[-3].token
			self.go_to_pos(bracket.pos, bracket.line)
			self.pos += len(bracket.content)
		
		colon: Token = tree[-2].token
		self.go_to_pos(colon.pos, colon.line)
		self.add(" do", 1)
		self.generate_block(tree[-1])
	
	def generate_simple_sentence(self, tree: ParentedTree):
		if len(tree) > 1:
			self.generate_sentence_body(tree[0])
	
	def generate_sentence_body(self, tree: ParentedTree):
		internal = tree[0]
		if internal.label() == "<any_expressions>":
			self.generate_any_expressions(internal)
		elif internal.label() == "<output>":
			self.generate_output(internal)
		elif internal.label() == "<assignment>":
			self.generate_assignment(internal)
		elif internal.label() == "<special_body>":
			self.generate_special_body(internal)
	
	def generate_special_body(self, tree: ParentedTree):
		first: Token = tree[0].token
		self.go_to(first)
		if first.content == "pass":
			self.skip(first)
		elif first.content == "return":
			self.add(first.content)
			self.generate_any_expressions(tree[1])
	
	def generate_length_expressions(self, tree: ParentedTree):
		first: Token = tree[0].token
		self.go_to(first)
		self.add("#", len(first.content))
		self.generate_token(tree[1])
		content = tree[2]
		if content.label() == "<function_call>":
			self.generate_function_call(content)
		elif content.label() == "<Identifier>":
			self.generate_terminal(content)
		elif content.label() == "<collection>":
			self.generate_collection(content)
		self.generate_token(tree[3])
	
	def generate_assignment(self, tree: ParentedTree):
		self.generate_terminal(tree[0])
		self.generate_token(tree[1])
		self.generate_any_expressions(tree[2])
	
	def generate_output(self, tree: ParentedTree):
		self.generate_token(tree[0])
		self.generate_token(tree[1])
		self.generate_any_expressions(tree[2])
		self.generate_token(tree[3])
	
	def generate_expressions(self, tree: ParentedTree):
		self.generate_any_expressions(tree[0])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_expressions(tree[2])
	
	def generate_any_expressions(self, tree: ParentedTree):
		internal = tree[0]
		if internal.label() == "<Identifier>":
			self.generate_terminal(internal)
		elif internal.label() == "<String_expressions>":
			self.generate_string_expressions(internal)
		elif internal.label() == "<mathematical_expressions>":
			self.generate_mathematical_expressions(internal)
		elif internal.label() == "<boolean_expressions>":
			self.generate_boolean_expression(internal)
		elif internal.label() == "<function_call>":
			self.generate_function_call(internal)
		elif internal.label() == "<collection>":
			self.generate_collection(internal)
	
	def generate_boolean_expression(self, tree: ParentedTree):
		first = tree[0]
		if isinstance(first, ParentedTree):
			if first.label() == "<boolean>":
				token = first[0].token
				self.go_to(token)
				self.add(token.content.lower())
			elif first.label() == "<Identifier>":
				self.generate_terminal(first)
			elif first.label() == "<function_call>":
				self.generate_function_call(first)
			elif first.label() == "<comparison_expressions>":
				self.generate_comparison_expressions(first)
			else:
				op = tree[1][0]
				self.generate_boolean_expression(tree[0])
				if isinstance(op, ParentedTree):
					self.generate_equivalence_operations(op)
				else:
					self.go_to(op.token)
					self.add(op.token.content)
				self.generate_boolean_expression(tree[2])
		elif first.token.content == "not":
			self.generate_token(first)
			self.generate_boolean_expression(tree[1])
	
	def generate_comparison_expressions(self, tree: ParentedTree):
		first = tree[0]
		if first.label() == "<mathematical_expressions>":
			self.generate_mathematical_expressions(tree[0])
			self.generate_comparison_operations(tree[1])
			self.generate_mathematical_expressions(tree[2])
		elif first.label() == "<String_expressions>":
			self.generate_string_expressions(tree[0])
			self.generate_equivalence_operations(tree[1])
			self.generate_string_expressions(tree[2])
	
	def generate_mathematical_expressions(self, tree: ParentedTree):
		self.generate_first_priority(tree[0])
	
	def generate_string_expressions(self, tree: ParentedTree):
		if len(tree) > 1:
			self.generate_string_expressions(tree[0])
			self.generate_token(tree[1])
			self.generate_string_expressions(tree[2])
		else:
			internal = tree[0]
			if internal.label() == "<String>":
				self.generate_terminal(internal)

	def generate_collection(self, tree: ParentedTree):
		if isinstance(tree[0], ParentedTree):
			if tree[0].label() == "<Identifier>":
				self.generate_terminal(tree[0])
			else:
				self.generate_function_call(tree[0])
		else:
			first: Token = tree[0].token
			self.go_to(first)
			if len(tree) == 2 or (len(tree) == 3 and tree[0].token.content == "dict"):
				self.skip(tree[-1])
				self.add("{}", 0)
			else:
				if first.content == "dict":
					self.skip(first)
					self.go_to(tree[1].token)
					self.add("{")
					self.generate_named_expression(tree[2])
					self.go_to(tree[3].token)
					self.add("}")
				elif first.content == "[":
					self.add("{")
					self.generate_collection_expressions(tree[1])
					self.go_to(tree[2].token)
					self.add("}")
				else:
					self.generate_token(tree[0])
					if tree[1].label() == "<expressions>":
						self.generate_collection_expressions(tree[1])
					else:
						self.generate_matches(tree[1])
					self.generate_token(tree[2])
	
	def generate_matches(self, tree: ParentedTree):
		match = tree[0]
		self.go_to(match[0].leaves()[0].token)
		self.add("[", 0)
		self.generate_left_expressions(match[0])
		self.add("]", 0)
		self.go_to(match[1].token)
		self.add(" =", 1)
		self.generate_any_expressions(match[2])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_matches(tree[2])
		
	def generate_left_expressions(self, tree: ParentedTree):
		self.generate_any_expressions(tree)
	
	def generate_collection_expressions(self, tree: ParentedTree, index=0):
		self.go_to(tree[0].leaves()[0].token)
		self.add("[" + str(index) + "] = ", 0)
		self.generate_any_expressions(tree[0])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_collection_expressions(tree[2], index + 1)
	
	def generate_named_expression(self, tree: ParentedTree):
		self.generate_assignment(tree[0])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_named_expression(tree[2])
	
	def generate_function_call(self, tree: ParentedTree):
		self.generate_terminal(tree[0])
		self.generate_token(tree[1])
		if len(tree) > 3:
			self.generate_expressions(tree[2])
		self.generate_token(tree[-1])
	
	def generate_identifiers(self, tree: ParentedTree):
		id_token: Token = tree[0][0].token
		self.go_to_pos(id_token.pos, id_token.line)
		self.add(id_token.content)
		if len(tree) > 1:
			self.add(",")
			self.generate_identifiers(tree[2])
	
	def generate_comparison_operations(self, tree: ParentedTree):
		internal = tree[0]
		if isinstance(internal, ParentedTree):
			self.generate_equivalence_operations(internal)
		else:
			token = internal.token
			self.go_to(token)
			self.add(token.content)
	
	def generate_equivalence_operations(self, tree: ParentedTree):
		token: Token = tree[0].token
		self.go_to(token)
		if token.content == "!=":
			self.add("~=")
		else:
			self.add(token.content)
	
	def generate_first_priority(self, tree: ParentedTree):
		self.generate_second_priority(tree[0])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_first_priority(tree[2])
	
	def generate_second_priority(self, tree: ParentedTree):
		self.generate_third_priority(tree[0])
		if len(tree) > 1:
			self.generate_token(tree[1])
			self.generate_second_priority(tree[2])
	
	def generate_third_priority(self, tree: ParentedTree):
		self.generate_fourth_priority(tree[0])
		if len(tree) > 1:
			token: Token = tree[1].token
			self.go_to(token)
			self.add("^", 2)
			self.generate_third_priority(tree[2])
	
	def generate_fourth_priority(self, tree: ParentedTree):
		if len(tree) > 1:
			self.generate_token(tree[0])
			self.generate_first_priority(tree[1])
			self.generate_token(tree[2])
		else:
			internal = tree[0]
			if internal.label() == "<Number>" or internal.label() == "<Identifier>":
				self.generate_terminal(internal)
			elif internal.label() == "<function_call>":
				self.generate_function_call(internal)
			elif internal.label() == "<length_expressions>":
				self.generate_length_expressions(internal)
	
	def generate_terminal(self, tree: ParentedTree):
		self.generate_token(tree[0])
	
	def generate_token(self, tree_token: TreeToken):
		token = tree_token.token
		self.go_to_pos(token.pos, token.line)
		self.add(token.content)
	
	def add(self, text: str, move: int = -1):
		if move == -1:
			move = len(text)
		self.lua_code += text
		self.pos += move
	
	def skip(self, token: Token):
		self.pos = token.pos + len(token.content)
	
	def newline(self, indentation=0):
		self.lua_code += "\n" + " " * indentation
		self.line += 1
		self.pos = indentation
	
	def go_to(self, token: Token):
		self.go_to_pos(token.pos, token.line)
	
	def go_to_pos(self, pos: int, line: int):
		if line == -1:
			line = self.line
		if pos == -1:
			pos = self.pos
		
		if line > self.line:
			self.lua_code += "\n" * (line - self.line)
			self.line = line
			self.pos = 0
		
		if pos > self.pos:
			self.lua_code += " " * (pos - self.pos)
			self.pos = pos
