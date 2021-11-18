import pyforms
from   pyforms          import BaseWidget
from   pyforms.controls import ControlTextArea
from   pyforms.controls import ControlButton


class Main(BaseWidget):

    def __init__(self):
        super(Main,self).__init__('Lupy Translator v0.0.1')

        self.formset = [('_python_code', '_lua_code'),'_translate_button', '_errors']
        self._python_code = ControlTextArea('Input Python code')
        self._errors = ControlTextArea('Errors:')
        self._translate_button = ControlButton('Translate')
        self._lua_code = ControlTextArea('Output Lua code')



#Execute the application
if __name__ == "__main__":   pyforms.start_app( Main, geometry=(200, 200, 900, 600) )


