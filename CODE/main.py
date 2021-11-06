from os import listdir
from os.path import isfile, join

from generator import generate
from lexical import LexicalAnalyzer
from syntactic import EarleyParser
from semantic import SemanticAnalyzer
from exceptions import AnalyzerError

analyzer = LexicalAnalyzer()


def translate(code):
	tokens = analyzer.parse(code)
	tree = EarleyParser(tokens).parse()
	SemanticAnalyzer(tree).check_tree()
	return generate(tokens)


def main():
	print("Translation started")
	print("Looking for .py files in input dir")
	files = [join("input", file) for file in listdir("input") if isfile(join("input", file)) and file.endswith(".py")]
	print("Files found: ")
	for file in files:
		name = file[6:]
		print("  -", name)
	print()
	for file in files:
		name = file[6:]
		print("Processing file:", name)
		py_code = open(file, "r").read()
		error = None
		try:
			lua_code = translate(py_code)
		except AnalyzerError as e:
			error = e
		
		print("Status:", "SUCCESS" if error is None else "ERROR")
		if error is None:
			filename = "output/" + file[6:-2] + "lua"
			print("Lua code was saved to:", filename)
			open(filename, "w").write(lua_code)
		else:
			print("Description:", error)
			print("File skipped")
		print()


if __name__ == '__main__':
	main()
