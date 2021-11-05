import sys
from io import StringIO

from lupa import LuaRuntime


def execute_python(code, globals = globals(), locals = locals()):
	out = sys.stdout
	io = StringIO()
	error = None
	try:
		sys.stdout = io
		exec(code, globals, locals)
		
	except BaseException as e:
		error = e
	sys.stdout = out
	if error is None:
		return io.getvalue()
	else:
		raise error


def execute_lua(code):
	lua_runtime = LuaRuntime()
	custom_output = """output = ""
	function print(text) output = output .. text .. "\\n" end\n"""
	lua_runtime.execute(custom_output + code)
	return lua_runtime.eval("output")