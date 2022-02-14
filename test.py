from errors import SyntacticError
from lupy import analyzer, EarleyParser
from lexer import Type, TokenIdentifier, TokenKeyword, TokenOperator, TokenNumber, TokenDivider, TokenString, \
	TokenIndent, LexicalError
from semantics import SemanticError, SemanticAnalyzer
import unittest


class TestLexical(unittest.TestCase):
	def test_identifier(self):
		code_text = r"""some_variable_name"""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenIdentifier, "This is not an instance of TokenIdentifier class")
		self.assertIs(received.type(), Type.Identifier, "This token's token type is not Identifier")
		self.assertEqual(received.content, "some_variable_name", "This token's content is not correct")

	def test_keyword(self):
		code_text = r"""True"""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenKeyword, "This is not an instance of TokenKeyword class")
		self.assertIs(received.type(), Type.Keyword, "This token's token type is not Keyword")
		self.assertEqual(received.content, "True", "This token's content is not correct")

	def test_operator(self):
		code_text = r"""*"""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenOperator, "This is not an instance of TokenOperator class")
		self.assertIs(received.type(), Type.Operator, "This token's token type is not Operator")
		self.assertEqual(received.content, "*", "This token's content is not correct")

	def test_number(self):
		code_text = r"""42.354e-42"""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenNumber, "This is not an instance of TokenNumber class")
		self.assertIs(received.type(), Type.Number, "This token's token type is not Number")
		self.assertEqual(received.content, "42.354e-42", "This token's content is not correct")

	def test_divider(self):
		code_text = r"""("""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenDivider, "This is not an instance of TokenDivider class")
		self.assertIs(received.type(), Type.Divider, "This token's token type is not Divider")
		self.assertEqual(received.content, "(", "This token's content is not correct")

	def test_string(self):
		code_text = r"""'string'"""
		received = analyzer.parse(code_text)[0]
		self.assertIsInstance(received, TokenString, "This is not an instance of TokenString class")
		self.assertIs(received.type(), Type.String, "This token's token type is not String")
		self.assertEqual(received.content, "'string'", "This token's content is not correct")

	def test_indent(self):
		code_text = r"""
	some_text
"""
		received = analyzer.parse(code_text)[1]
		self.assertIsInstance(received, TokenIndent, "This is not an instance of TokenIndent class")
		self.assertIs(received.type(), Type.Divider, "This token's token type is not Divider")
		self.assertEqual(received.content, "indent", "This token's content is not correct")

	def test_dedent(self):
		code_text = r"""
	some_text
"""
		received = analyzer.parse(code_text)[4]
		self.assertIsInstance(received, TokenIndent, "This is not an instance of TokenIndent class")
		self.assertIs(received.type(), Type.Divider, "This token's token type is not Divider")
		self.assertEqual(received.content, "dedent", "This token's content is not correct")

	def test_unknown_symbol_error(self):
		code_text = r"""a = 1
print(a) # here comes some comment"""
		self.assertRaises(LexicalError, analyzer.parse, code_text)
		assertion = False
		try:
			analyzer.parse(code_text)
		except LexicalError as e:
			if e.message == """Lexical Error
Incorrect code in position 10 line 2: print(a) # here comes some comment
                                               ↑""":
				assertion = True
		self.assertTrue(assertion, "This code produce LexicalError in a wrong place")


class TestSyntactic(unittest.TestCase):
	def test_incorrect_chain(self):
		code_text = r"""
a := 1
print(a)
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		self.assertRaises(SyntacticError, parser.parse)

	def test_correct_chain(self):
		code_text = r"""
a = 1
print(a)
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		tree = parser.parse()
		self.assertIsNotNone(tree, "This code chain is not correct")

	def test_empty_func(self):
		code_text = r"""
a = 1
print(a)

def foo():
	pass
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		tree = parser.parse()
		self.assertIsNotNone(tree, "This code chain is not correct")

	def test_func_with_multiple_arguments(self):
		code_text = r"""
a = 1
print(a)

def foo():
	pass
	
def baz(f, c, m):
	print(f)

baz(a, a, a)

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		tree = parser.parse()
		self.assertIsNotNone(tree, "This code chain is not correct")


class TestSemantic(unittest.TestCase):
	def test_correct_program(self):
		code_text = r"""
a = 1
print(a)
b = 42

def foo():
	print(a)
	c = 3

def baz(a, b):
	print(b)
	z = 15

print(b)
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()

	def test_incorrect_identifier(self):
		code_text = r"""
a = 1
print(a)
b = 42

def foo():
	print(a)
	c = 3

def baz(a, b):
	print(b)
	z = 15

print(z)
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		self.assertRaises(SemanticError, semantic_analyzer.check_tree)

	def test_correct_function_call(self):
		code_text = r"""
a = 1
print(a)
b = 42

def foo():
	print(a)
	c = 3

def baz(a, b):
	print(b)
	z = 15
	
	print(z)

foo()
baz(a, a)

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()

	def test_incorrect_function_call(self):
		code_text = r"""
a = 1
print(a)
b = 42

def foo():
	print(a)
	c = 3

def baz(a, b):
	print(b)
	z = 15
	print(z)

foo(a)

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		self.assertRaises(SemanticError, semantic_analyzer.check_tree)

	def test_global_var_before_calling_predefined_func(self):
		code_text = r"""
def foo():
	print(a)

a = "test"
foo()

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()

	def test_new_parameter_in_for_cycle(self):
		code_text = r"""
for i in {1, 2, 3}:
	print(i)
	
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()

	def test_func_redefinition(self):
		code_text = r"""
def foo():
	print(a)

a = "test"
foo()

def foo():
	print(b)
foo()

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		self.assertRaises(SemanticError, semantic_analyzer.check_tree)

	def test_func_redefinition_with_parameters(self):
		code_text = r"""
def func(par1, par2):
	return par1 + par2

def func(par1, par2):
	return par1 + par2

func = func(2, 2)

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())

	def test_func_call_before_definition(self):
		code_text = r"""
def foo():
	bar()
	
def bar():
	pass

foo()

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		try:
			semantic_analyzer.check_tree()
		except SemanticError as error:
			self.assertEqual(error.token.line, 8)
			self.assertEqual(error.token.pos, 0)

	def test_func_call_with_func_pointers(self):
		code_text = r"""
def foo(a, b):
	bar()


def bar():
	pass


foo(bar, bar)

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()

	def test_func_call_with_variable(self):
		code_text = r"""
def foo():
	bar()


def bar():
	pass


a = foo
a()

"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()


	def test_call_param_as_func(self):
		code_text = r"""
def foo(a, b):
	b(1)

def bar(a):
	print(1)

foo(1, bar)
"""
		tokens = analyzer.parse(code_text)
		parser = EarleyParser(tokens)
		semantic_analyzer = SemanticAnalyzer(parser.parse())
		semantic_analyzer.check_tree()


if __name__ == '__main__':
	unittest.main()
