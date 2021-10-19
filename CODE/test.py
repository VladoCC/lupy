from CODE.main import translate


def run_tests():
	# 0 test case
	code_text = r"""
42.354e-42 * 9.2e+1 = True
"""
	translate(code_text)

	# 1 test case
	code_text = r"""
print("Hello, world!")
"""
	translate(code_text)

	# 2 test case
	code_text = r"""
a = 2
b = 3
print(a + b)
"""
	translate(code_text)

	# 3 test case
	code_text = r"""
username = 'John'
magic_number = 3.14159e+0
if (magic_number > 4):
	print("What's happen?")
else:
	print(len(username))
"""
	translate(code_text)


if __name__ == '__main__':
	run_tests()
