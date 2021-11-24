import pyforms
from pyforms import BaseWidget
from pyforms.controls import ControlTextArea
from pyforms.controls import ControlButton

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


class Main(BaseWidget):

    def __init__(self):
        super(Main,self).__init__('Lupy Translator v0.0.1')

        self.formset = [('_python_code', '_lua_code'),'_translate_button', '_errors']
        self._python_code = ControlTextArea('Input Python code')
        self._errors = ControlTextArea('Errors:')
        self._translate_button = ControlButton('Translate')
        self._lua_code = ControlTextArea('Output Lua code')

        self._translate_button.value = self.trans_click

    def trans_click(self):
        errors = None
        lua_code = ''
        try:
            lua_code = translate(self._python_code.value)
        except AnalyzerError as e:
            errors = e

        if errors is None:
            self._lua_code.value = lua_code
            self._errors.value = ''
        else:
            self._lua_code.value = ''
            self._errors.value = errors


if __name__ == "__main__": pyforms.start_app(Main, geometry=(200, 200, 900, 600))
