from collections import defaultdict
from nltk.tree import Tree
import re


class Rule(object):
	def __init__(self, lhs, rhs):
		# Represents the rule 'lhs -> rhs', where lhs is a non-terminal and
		# rhs is a list of non-terminals and terminals.
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
	def __init__(self):
		# The rules are represented as a dictionary from L.H.S to R.H.S.
		self.rules = defaultdict(list)

	def add(self, rule):
		self.rules[rule.lhs].append(rule)

	@staticmethod
	def load_grammar(file):

		grammar = Grammar()

		with open(file) as f:
			for line in f:
				line = line.strip()

				if len(line) == 0 or re.search(r"^\s*#", line):
					continue

				line = line.split('#')[0]
				entries = line.split('->')
				lhs = entries[0].strip()
				for rhs in entries[1].split('|'):
					grammar.add(Rule(lhs, rhs.strip().split()))

		return grammar

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		s = [str(r) for r in self.rules['S']]

		for nt, rule_list in self.rules.iteritems():
			if nt == 'S':
				continue

			s += [str(r) for r in rule_list]

		return '\n'.join(s)

	# Returns the rules for a given Non-terminal.
	def __getitem__(self, nt):
		return self.rules[nt]

	def is_terminal(self, sym):
		return len(self.rules[sym]) == 0

	def is_tag(self, sym):
		if not self.is_terminal(sym):
			return all(self.is_terminal(s) for r in self.rules[sym] for s in
			           r.rhs)

		return False


class EarleyState(object):
	GAM = '<GAM>'

	def __init__(self, rule, dot=0, sent_pos=0, chart_pos=0, back_pointers=None):
		# CFG Rule.
		if back_pointers is None:
			back_pointers = []
		self.rule = rule
		# Dot position in the rule.
		self.dot = dot
		# Sentence position.
		self.sent_pos = sent_pos
		# Chart index.
		self.chart_pos = chart_pos
		# Pointers to child states (if the given state was generated using
		# Completer).
		self.back_pointers = back_pointers

	def __eq__(self, other):
		if type(other) is EarleyState:
			return self.rule == other.rule and self.dot == other.dot and \
			       self.sent_pos == other.sent_pos

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

	@staticmethod
	def init():
		return EarleyState(Rule(EarleyState.GAM, ['S']))


class ChartEntry(object):
	def __init__(self, states):
		# List of Earley states.
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
	def __init__(self, entries):
		# List of chart entries.
		self.entries = entries

	def __getitem__(self, i):
		return self.entries[i]

	def __len__(self):
		return len(self.entries)

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '\n\n'.join([("Chart[%d]:\n" % i) + str(entry) for i, entry in
		                    enumerate(self.entries)])

	@staticmethod
	def init(l):
		return Chart([(ChartEntry([]) if i > 0 else
		               ChartEntry([EarleyState.init()])) for i in range(l)])


class EarleyParser(object):
	def __init__(self, sentence, grammar=Grammar.load_grammar("grammar\\grammar.txt")):
		self.words = sentence.split()
		self.grammar = grammar

		self.chart = Chart.init(len(self.words) + 1)

	def predictor(self, state, pos):
		for rule in self.grammar[state.next()]:
			self.chart[pos].add(EarleyState(rule, dot=0,
			                                sent_pos=state.chart_pos, chart_pos=pos))

	def scanner(self, state, pos):
		if state.chart_pos < len(self.words):
			word =  self.words[pos] if len(self.words) > pos else ""

			if word == state.next():
				self.chart[pos + 1].add(EarleyState(state.rule,
				                                    dot=state.dot + 1, sent_pos=state.chart_pos,
				                                    chart_pos=(state.chart_pos),
				                                    back_pointers = state.back_pointers))

	def completer(self, state, pos):
		for prev_state in self.chart[state.chart_pos]:
			if prev_state.next() == state.rule.lhs:
				test = (prev_state.back_pointers + [state])
				self.chart[pos].add(EarleyState(prev_state.rule,
				                                dot=(prev_state.dot + 1), sent_pos=prev_state.chart_pos,
				                                chart_pos=prev_state.chart_pos,
				                                back_pointers=(prev_state.back_pointers + [state])))

	def parse(self):
		def is_terminal(state):
			return self.grammar.is_terminal(state.next())

		for i in range(len(self.words) + 1):
			for state in self.chart[i]:
				if not state.is_complete():
					if is_terminal(state):
						self.scanner(state, i)
					else:
						self.predictor(state, i)
				else:
					self.completer(state, i)

	def has_parse(self):
		for state in self.chart[-1]:
			if state.is_complete() and state.rule.lhs == 'S' and \
				state.sent_pos == 0 and state.chart_pos == len(self.words):
				return True

		return False

	def get(self):
		def get_helper(state):
			if len(state.back_pointers) == 0:
				return Tree(state.rule.lhs, state.rule.rhs)

			children = []
			for s in state.rule.rhs:
				pointer = None
				for p in state.back_pointers:
					if p.rule.lhs == s:
						pointer = p
						break
				children.append(s if pointer is None else get_helper(pointer))
			return Tree(state.rule.lhs, children)

		for state in self.chart[-1]:
			if state.is_complete() and state.rule.lhs == 'S':
				return get_helper(state)

		return None
