# LuPy
## What is this project?
LuPy is a simple translator that produces Lua equivalent for a subset of Python programs.   
It supports most of the script-like yntax of Python, i.e anything without classes and imports.   
It also doesnt support [stray expressions](#stray-expressions), since they aren't allowed in Lua.

### Standard library
For now LuPy supports only a few functions from standard library:
`print()` - translates to itself in Lua.   
`dict()` - translates into table declaration.
`len()` - translates into `#`, which when placed before table returns length of it.   
   
Any other function are not officially supported, but would work in [unsafe mode](#sematics-and-safe-mode) if they have the same name in both languages. For example `type()` function works like that.

### Python collections vs Lua tables
LuPy translates all the collections (lists, dictionaries) from Python into Lua tables. 
Since Python arrays start from zero and their Lua counterpart start from one, LuPy explicitly defines that the first element of array starts from zero in translated Lua code. 

### Stray expressions
Stray expressions, e.g. expressions without assignment are semantically incorrect for Lua, thus LuPy doesn't translate programs with them.

**Example:**
```python
# allowed
a = 2 + 2

# allowed
func()

# forbidden
2 + 2
```

## Installation
This project stores dependencies in `requirements.txt` file.   
To install them use:
```
pip install -r requirements.txt
```

## Usage
### Command line
```
python main.py -i ./input -o ./output
```
**Arguments:**   
`-i <path>` - path to input file or directory. Default: './input'.   
`-o <path>` - path to output directory. Default: './output.   
`-unsafe` - turns off semantical checks

### Python
To translate string:
```python
from lupy import translate

translate("print('Hello World!')")
```

To process file or folder:
```python
from lupy import process

# process one file and save to working dir
process("test.py" "./")
# process ./input folder and save result into ./output folder
process("./input", "./output")
```

## Implementation
### Lexer
LuPy uses [regular expression](https://en.wikipedia.org/wiki/Regular_expression) based lexer for converting python code into tokens.   
Lexer also does all the preprocessing of data, converting names (e.g. identifiers, function names, numbers, strings and etc.) into easily parsable tokens, since only type of this tokens is importnant and content can be ommited for parsing stage.

### Parser
LuPy uses [Earley Parser](https://en.wikipedia.org/wiki/Earley_parser) for checking that input is a part of supported subset of Python and building [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) of the program.   
You can find grammar used in LuPy: [here](https://github.com/VladoCC/lupy/blob/main/grammar/grammar.txt).   

### Sematics and Safe mode
LuPy does a list of checks on AST before generating a Lua program from it to ensure semantical correctness of original code. 
This stage can be skipped by running LuPy in [unsafe mode](#command-line).

**Checks:**
* Variable must be declared (i.e. assigned) before it's used in expressions.
* Function must be declared before it's called for the first time
* Function call must have the same amount of parameters as function declaration (default values aren't supported in LuPy)
* When function is called all variables used by this function (i.e. global scope variables) must be declared
* When function is called all the functions called inside of it must be declared 
