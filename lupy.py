import os
import sys
from os import listdir
from os.path import isfile, join

from nltk import ParentedTree

from generator import Generator
from lexer import LexicalAnalyzer
from parse import EarleyParser
from semantics import SemanticAnalyzer
from errors import AnalyzerError


analyzer = LexicalAnalyzer()
generator = Generator()


def translate(code, safe=True):
	tokens = analyzer.parse(code)
	tree = ParentedTree.convert(EarleyParser(tokens).parse())
	if safe:
		SemanticAnalyzer(tree).check_tree()
	return generator.generate(tree)


def main():
	args = sys.argv
	args.pop(0)
	input = None
	output = None
	safe = True
	help = len(args) > 0
	while len(args) > 0:
		arg = args.pop(0)
		if arg == "-i":
			if len(args) > 0:
				input = args.pop(0)
				help = False
		elif arg == "-o":
			if len(args) > 0:
				output = args.pop(0)
				help = False
		elif arg == "-unsafe":
			safe = False
			help = False
		else:
			break
	
	if help:
		show_help()
	else:
		if input is None:
			input = "./input"
		if output is None:
			output = "./output"
		process(input, output, safe)


def show_help():
	print("Help:")
	print("  -i <path> - path to input file or directory. Default: `./input`")
	print("  -o <path> - path to output directory. Default: `./output`")


def process(input, output, safe=True):
	print("Translation started")
	print("Looking for .py files in {} dir".format(input))
	files = []
	if os.path.isdir(input):
		files = [(join(dirpath, file), file) for dirpath, _, filenames in os.walk(input) for file in filenames if isfile(join(dirpath, file)) and file.endswith(".py")]
	elif os.path.isfile(input):
		files.append(input)
	else:
		print("Error: input file/dir not found")
		print()
		show_help()
		exit(-1)
	print("Files found: ")
	for _, filename in files:
		print("  -", filename)
	print()
	for path, filename in files:
		print("Processing file:", filename)
		py_code = open(path, "r").read()
		error = None
		try:
			lua_code = translate(py_code, safe)
		except AnalyzerError as e:
			error = e
		
		if not os.path.exists(output):
			os.mkdir(output)
		print("Status:", "SUCCESS" if error is None else "ERROR")
		if error is None:
			filename = "{}/".format(output) + filename[:-2] + "lua"
			print("Lua code was saved to:", filename)
			open(filename, "w").write(lua_code)
		else:
			print("Description:", error)
			print("File skipped")
		print()


if __name__ == '__main__':
	main()
