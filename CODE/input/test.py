def test(a, b, c, d):
	pass
	for i in range(4):
		if i % 2 == 0:
			print(i)

def test2():
	for i in range(1, 10):
		if i % 2 == 0:
			print(i)

def test3():
	for i in range(1, 45 % 5):
		if i % 2 == 0:
			print(i)

def foo(a):
	print(a)
	b = 3 * a
	return a + 2

def bar(a):
	if a % 3 == 1: print(a)
	else: print(0)

def bar2(a):
	if not a(a): print(a)
	else: print(0)

def bar3(a):
	if True: print(a)
	else: print(0)

def bar4(a):
	if not a: print(a)
	else: print(0)

def bar5(a):
	if a != a: print(a)
	else: print(0)

def bar6(a):
	if a and a: print(a)
	else: print(0)

def bar7(a):
	if a <= 5: print(a)
	else: print(0)

def another():
	for i in [1, 2, 3]:
		print(i)

print("hello" + "world")
len(test(1, 2, 3, 4))
a = dict(test=1, t=2)
b = [1, 2]
c = {0: 1, test(a, a, a, a): 2}
