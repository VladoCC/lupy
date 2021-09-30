from enum import Enum
import re


# СЕКЦИЯ С ГОВНОКОДОМ
# float number regex: [+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)

class Type(Enum):
  Ident = 0
  Num = 1
  String = 2
  Op = 3
  Div = 4
  Const = 5
  KeyWord = 6


class Token:
  token_type = Type.Const
  content = ""
  line = 0
  pos = 0

  def __str__(self):
    return """Token:
      token_type = {}
      content = {}
      line = {}
      position = {}""".format(
      self.token_type,
      self.content,
      self.line,
      self.pos)


class TokenDiv(Token):

  def __init__(self, symbol: str, line: int, pos: int):
    self.token_type = Type.Div
    self.content = symbol
    self.line = line
    self.pos = pos


class TokenIndent(Token):

  def __init__(self, indent: bool, line: int, pos: int):
    self.token_type = Type.Div
    self.content = "indent" if indent else "dedent"
    self.line = line
    self.pos = pos


class AbstractPattern:
  regex = ""

  def token(self, match: str, pos: int, line: int):
    token = Token()
    token.pos = pos
    token.line = line
    return token


class PatternNumber(AbstractPattern):
  regex = r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)"

  def token(self, match: str, pos: int, line: int):
    token = super().token(match, pos, line)
    token.token_type = Type.Num
    token.content = match
    return token

class PatternDiv(AbstractPattern):
  regex = r",|(|){|}|:"

  def token(self, match: str, pos: int, line: int):
    token = super().token(match, pos, line)
    token.token_type = Type.Num
    token.content = match
    return token

patterns = [PatternNumber(), PatternDiv()]


def main(text):
  print("Code: \n", text)
  tokens = []
  pos = 0
  line = 0
  indent_level = 0
  while len(text) > 0:
    suc = False
    for pattern in patterns:
      res = re.search("^" + pattern.regex, text)
      if res is not None:
        endpos = res.regs[0][1]
        token = pattern.token(text[0:endpos], line, pos)
        text = text[endpos:]
        suc = True
        tokens.append(token)
        pos += endpos
        break

    if not suc:
      res = re.match("\n", text)
      if res is not None:
        text = text[1:]
        tokens.append(TokenDiv('newline', line, pos))
        pos = 0
        line += 1

        res = re.search("^ +", text)
        if res is not None:
          endpos = res.regs[0][1]
        else:
          endpos = 0
        for i in range(abs(endpos - indent_level)):
          tokens.append(TokenIndent(endpos > indent_level, line, pos))
          pos += 1
        indent_level = endpos
        text = text[endpos:]

        suc = True

    if not suc:
      res = re.search("^ +", text)
      if res is not None:
        endpos = res.regs[0][1]
        pos += endpos
        text = text[endpos:]
        suc = True

  for token in tokens:
    print(token)


def run_tests():
  # 0 test case
  code_text = u"""
  42.354e-42
"""
  main(code_text)
  # 1 test case
  code_text = r"""
  print("Hello, world!")
  """
  main(code_text)
  # 2 test case
  code_text = r"""
  a = 2
  b = 3
  print(a + b)
  """
  main(code_text)
  # 3 test case
  code_text = r"""
  username = 'John'
  magic_number = 3.14159e+0
  if (magic_number > 4):
    print("What's happen?")
  else:
    print(len(username))
   """
  main(code_text)


if __name__ == '__main__':
  run_tests()

# КОНЕЦ СЕКЦИИ С ГОВНОКОДОМ
