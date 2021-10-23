from os import listdir
from os.path import isfile, join

from CODE.lexical import LexicalAnalyzer
from CODE.syntactic import EarleyParser

analyzer = LexicalAnalyzer()


def translate(code):
	tokens = analyzer.parse(code)
	token_line = ""
	for token in tokens:
		token_line += token.as_symbol() + " "
	token_line = token_line[:-1]

	print(token_line)

	parser = EarleyParser(token_line)
	parser.parse()
	tree = parser.get()
	if tree is not None:
		tree.draw()
	else:
		print("can't parse code: \n", code)

	return ""

if __name__ == '__main__':
	files = [join("input", file) for file in listdir("input") if isfile(join("input", file)) and file.endswith(".py")]
	for file in files:
		py_code = open(file, "r").read()
		lua_code = translate(py_code)
		print(lua_code)
		open("output\\" + file[5:-2] + "lua", "w").write(lua_code)
