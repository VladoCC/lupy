import sys
from io import StringIO

from lupa import LuaRuntime


def execute_python(code, globals = globals(), locals = locals()):
	try:
		out = sys.stdout
		io = StringIO()
		sys.stdout = io
		exec(code, globals, locals)
		sys.stdout = out
		return io.getvalue()
	except:
		raise RuntimeError("Unable to execute python code")


def execute_lua(code):
	try:
		lua_runtime = LuaRuntime()
		custom_output = """output = ""
		function print(text) output = output .. text .. "\\n" end\n"""
		lua_runtime.execute(custom_output + code)
		return lua_runtime.eval("output")
	except:
		raise RuntimeError("Unable to execute lua code")