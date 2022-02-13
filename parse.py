from collections import defaultdict
from nltk.tree import Tree
import re

from errors import SyntacticError, NoNewLineError


class Rule(object):
	def __init__(self, lhs, rhs):
		self.lhs, self.rhs = lhs, rhs

	def __contains__(self, sym):
		return sym in self.rhs

	def __eq__(self, other):
		if type(other) is Rule:
			return self.lhs == other.lhs and self.rhs == other.rhs
		return False

	def __getitem__(self, i):
		return self.rhs[i]

	def __len__(self):
		return len(self.rhs)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return self.lhs + ' -> ' + ' '.join(self.rhs)


class Grammar(object):
	def __init__(self, filepath="grammar/grammar.txt"):
		self.rules = defaultdict(list)
		with open(filepath, "r") as f:
			for line in f:
				line = line.strip()

				if len(line) == 0 or re.search(r"^\s*#", line):
					continue

				line = line.split('#')[0]
				entries = line.split('->')
				lhs = entries[0].strip()
				for rhs in entries[1].split('|'):
					self.add(Rule(lhs, rhs.strip().split()))

	def add(self, rule):
		self.rules[rule.lhs].append(rule)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		s = [str(r) for r in self.rules['S']]

		for nt, rule_list in self.rules.items():
			if nt == 'S':
				continue

			s += [str(r) for r in rule_list]

		return '\n'.join(s)

	def __getitem__(self, nt):
		return self.rules[nt]

	def is_terminal(self, sym):
		return len(self.rules[sym]) == 0

	def is_tag(self, sym):
		if not self.is_terminal(sym):
			return all(self.is_terminal(s) for r in self.rules[sym] for s in r.rhs)

		return False


class EarleyState(object):
	def __init__(self, rule=Rule("S", ["<program>"]), dot=0, sent_pos=0, chart_pos=0, back_pointers=None):
		if back_pointers is None:
			back_pointers = []
		self.rule = rule
		self.dot = dot
		self.sent_pos = sent_pos
		self.chart_pos = chart_pos
		self.back_pointers = back_pointers

	def __eq__(self, other):
		if type(other) is EarleyState:
			return self.rule == other.rule and self.dot == other.dot and self.sent_pos == other.sent_pos

		return False

	def __len__(self):
		return len(self.rule)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		def str_helper(state):
			return ('(' + state.rule.lhs + ' -> ' +
					' '.join(state.rule.rhs[:state.dot] + ['*'] +
							 state.rule.rhs[state.dot:]) +
					(', [%d, %d])' % (state.sent_pos, state.chart_pos)))

		return (str_helper(self) +
				' (' + ', '.join(str_helper(s) for s in self.back_pointers) + ')')

	def next(self):
		if self.dot < len(self):
			return self.rule[self.dot]

	def is_complete(self):
		return len(self) == self.dot
	
	def get_helper(self, tokens):
		children = []
		for s in self.rule.rhs:
			pointer = None
			index = -1
			for i in range(len(self.back_pointers)):
				p = self.back_pointers[i]
				if p.rule.lhs == s:
					pointer = p
					index = i
					break
			if pointer is None:
				token = TreeToken(tokens.pop(0))
				children.append(token if not s.startswith("<") else Tree(s, [token]))
			else:
				self.back_pointers.pop(index)
				children.append(pointer.get_helper(tokens))
		return Tree(self.rule.lhs, children)


class ChartEntry(object):
	def __init__(self, states):
		self.states = states

	def __iter__(self):
		return iter(self.states)

	def __len__(self):
		return len(self.states)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '\n'.join(str(s) for s in self.states)

	def add(self, state):
		if state not in self.states:
			self.states.append(state)


class Chart(object):
	def __init__(self, len):
		self.entries = [(ChartEntry([]) if i > 0 else ChartEntry([EarleyState()])) for i in range(len)]

	def __getitem__(self, i):
		return self.entries[i]

	def __len__(self):
		return len(self.entries)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '\n\n'.join([("Chart[%d]:\n" % i) + str(entry) for i, entry in enumerate(self.entries)])


class TreeToken:
	def __init__(self, token):
		self.token = token

	def __str__(self):
		return self.token.content


class EarleyParser(object):
	def __init__(self, tokens, grammar=Grammar()):
		self.tokens = tokens.copy()
		self.check_newline()
		sentence = ""
		for token in tokens:
			sentence += token.as_symbol() + " "
		sentence = sentence[:-1]
		self.words = sentence.split()
		self.grammar = grammar
		self.chart = Chart(len(self.words) + 1)

	def check_newline(self):
		success = False
		for i in range(len(self.tokens)):
			if self.tokens[-i - 1].content == "newline":
				success = True
				break
			elif self.tokens[-i - 1].content == "dedent":
				continue
			else:
				break
		if not success:
			raise NoNewLineError()

	def predictor(self, state, pos):
		for rule in self.grammar[state.next()]:
			self.chart[pos].add(EarleyState(rule, dot=0, sent_pos=state.chart_pos, chart_pos=pos))

	def scanner(self, state, pos):
		if state.chart_pos < len(self.words):
			word = self.words[pos] if len(self.words) > pos else ""

			if word == state.next():
				self.chart[pos + 1].add(EarleyState(state.rule,
													dot=state.dot + 1, sent_pos=state.chart_pos,
													chart_pos=(state.chart_pos),
													back_pointers=state.back_pointers))

	def completer(self, state, pos):
		for prev_state in self.chart[state.chart_pos]:
			if prev_state.next() == state.rule.lhs:
				test = (prev_state.back_pointers + [state])
				self.chart[pos].add(EarleyState(prev_state.rule,
												dot=(prev_state.dot + 1), sent_pos=prev_state.chart_pos,
												chart_pos=prev_state.chart_pos,
												back_pointers=(prev_state.back_pointers + [state])))

	def parse(self):
		for i in range(len(self.words) + 1):
			for state in self.chart[i]:
				if not state.is_complete():
					is_terminal = self.grammar.is_terminal(state.next())
					if is_terminal:
						self.scanner(state, i)
					else:
						self.predictor(state, i)
				else:
					self.completer(state, i)

		return self._get()

	def _get(self):
		for state in self.chart[-1]:
			if state.is_complete() and state.rule.lhs == 'S':
				return state.get_helper(self.tokens)

		raise SyntacticError
