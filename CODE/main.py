from os import listdir
from os.path import isfile, join

from generator import generate
from lexical import LexicalAnalyzer
from syntactic import EarleyParser
from semantic import SemanticAnalyzer, SemanticError

from lupa import LuaRuntime

analyzer = LexicalAnalyzer()

def translate(code):
	tokens = analyzer.parse(code)
	token_line = ""
	for token in tokens:
		token_line += token.as_symbol() + " "
	token_line = token_line[:-1]

	#print(token_line)

	parser = EarleyParser(tokens)
	parser.parse()
	tree = parser.get()

	if tree is not None:
		#tree.pretty_print()
		pass
	else:
		print("can't parse code: \n", code)

	semantic_analyzer = SemanticAnalyzer(tree)
	try:
		semantic_analyzer.check_tree()
	except SemanticError as semantic_error:
		print(semantic_error)

	return generate(tokens)


if __name__ == '__main__':
	files = [join("input", file) for file in listdir("input") if isfile(join("input", file)) and file.endswith(".py")]
	for file in files:
		py_code = open(file, "r").read()
		print("Python code: \n", py_code)
		print("Python execution output:")
		exec (py_code)
		lua_code = translate(py_code)
		print("\nLua code:")
		print(lua_code)
		lua_runtime = LuaRuntime()
		print("\nLua execution output:")
		lua_runtime.execute(lua_code)
		open("output/" + file[5:-2] + "lua", "w").write(lua_code)
