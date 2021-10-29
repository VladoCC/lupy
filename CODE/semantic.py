from collections import defaultdict
from nltk.tree import Tree, ParentedTree


class SemanticError(BaseException):
    pass


class SemanticAnalyzer(object):
    def __init__(self, tree: Tree):
        self.tree = ParentedTree.convert(tree)
        self.known_identifiers = {'<program>': set()}
        self.known_function_parameters = {}

    def get_identifiers_with_their_scope(self):
        return self.known_identifiers

    def get_functions_with_their_parameters(self):
        return self.known_function_parameters

    def check_tree(self):
        if not self.tree:
            raise SemanticError('Tree are not set.')
        self._check_identifiers()

    def _get_current_context(self, node: ParentedTree) -> str:
        while node.parent() and node.parent().label() != '<function>':
            node = node.parent()
        if node.parent() and node.parent().label() == '<function>':
            current_context = str(list(node.parent().subtrees())[0].leaves()[1])
            return current_context
        return '<program>'

    def _store_function_parameters(self, func: ParentedTree) -> None:
        self.known_function_parameters.setdefault(self._get_current_context(func), 0)
        for node in func.parent().subtrees():
            if node.parent().label() == '<Identifiers>' and node.label() == '<Identifier>':
                self.known_function_parameters[self._get_current_context(node)] += 1

    def _check_function_parameters(self, func: ParentedTree) -> None:
        current_context = str(func.leaves()[0])
        known_function_parameters = 0
        for node in func.subtrees():
            if node.label() == '<expressions>':
                known_function_parameters += 1
        current_known_parameters = self.known_function_parameters.get(current_context)
        if (current_known_parameters is None or
                current_known_parameters != known_function_parameters):
            raise SemanticError(
                'Parameters in the declaration and function call do not match:\n{}'.format(
                    str(func.leaves()[0].token)
                ))

    def _check_identifiers(self) -> None:
        for node in self.tree.subtrees():
            if not node.parent():
                continue
            elif node.label() == '<Identifier>':
                current_node_parent_label = node.parent().label()
                if current_node_parent_label == '<assignment>':
                    self.known_identifiers.setdefault(self._get_current_context(node), set()).add(
                        str(node.leaves()[0]))
                elif current_node_parent_label == '<function>':
                    self.known_identifiers[str(node.leaves()[0])] = set()
                    self._store_function_parameters(node)
                elif current_node_parent_label == '<Identifiers>':
                    self.known_identifiers[self._get_current_context(node)].add(str(node.leaves()[0]))
                elif current_node_parent_label == '<function_call>':
                    if str(node.leaves()[0]) not in self.known_identifiers:
                        raise SemanticError(
                            'The function identifier was used before it was announced:\n{}'.format(
                                str(node.leaves()[0].token)
                            ))
                    self._check_function_parameters(node.parent())
                else:
                    current_context = self.known_identifiers.get(self._get_current_context(node))
                    if ((not current_context or
                         str(node.leaves()[0]) not in current_context) and
                            str(node.leaves()[0]) not in self.known_identifiers['<program>']):
                        raise SemanticError(
                            'The identifier was encountered before it was announced:\n{}'.format(
                                str(node.leaves()[0].token)
                            ))
