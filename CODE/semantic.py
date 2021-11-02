from nltk.tree import Tree, ParentedTree
from lexical import Token
from exceptions import AnalyzerError


class SemanticError(AnalyzerError):
    def __init__(self, token: Token, *args):
        super(SemanticError, self).__init__(*args)
        self.token = token


class SemanticAnalyzer(object):
    def __init__(self, tree: Tree):
        self.tree = ParentedTree.convert(tree)
        self.known_identifiers = {'<program>': set()}
        self.known_function_parameters = {}
        self.identifiers_to_catch_in_function = {}
        self.function_identifiers_to_catch_in_function = {}

    def get_identifiers_with_their_scope(self):
        return self.known_identifiers

    def get_functions_with_their_parameters(self):
        return self.known_function_parameters

    def get_identifiers_to_catch_in_function(self):
        return self.identifiers_to_catch_in_function

    def check_tree(self):
        if not self.tree:
            raise SemanticError(Token(0, 0), 'Semantic Error\nTree isn\'t set.')
        self.__check_identifiers()

    def __get_current_context(self, node: ParentedTree) -> str:
        while node.parent() and node.parent().label() != '<function>':
            node = node.parent()
        if node.parent() and node.parent().label() == '<function>':
            current_context = str(list(node.parent().subtrees())[0].leaves()[1])
            return current_context
        return '<program>'

    def __store_function_parameters(self, func: ParentedTree) -> None:
        self.known_function_parameters.setdefault(self.__get_current_context(func), 0)
        for node in func.parent().subtrees():
            if node.parent().label() == '<Identifiers>' and node.label() == '<Identifier>':
                self.known_function_parameters[self.__get_current_context(node)] += 1

    def __check_function_parameters(self, func: ParentedTree) -> None:
        current_context = str(func.leaves()[0])
        known_function_parameters = 0
        for node in func.subtrees():
            if node.label() == '<expressions>':
                known_function_parameters += 1
        current_known_parameters = self.known_function_parameters.get(current_context)
        if (current_known_parameters is None or
                current_known_parameters != known_function_parameters):
            raise SemanticError(func.leaves()[0].token,
                                'Semantic Error\nParameters in the declaration and function call do not match:\n{}'.format(
                                    str(func.leaves()[0].token)
                                ))

    def __check_function_call_catch_identifiers(self, identifier_token: Token, func_name: str) -> None:
        current_variable_identifiers_to_catch = self.identifiers_to_catch_in_function.get(func_name)
        if current_variable_identifiers_to_catch:
            current_variable_identifiers_to_catch = self.identifiers_to_catch_in_function.get(func_name).copy()
        else:
            return None
        current_variable_identifiers_to_catch -= self.known_identifiers.get(func_name)
        current_variable_identifiers_to_catch -= self.known_identifiers.get('<program>')
        if current_variable_identifiers_to_catch:
            raise SemanticError(identifier_token,
                                "Semantic Error\nWhen the function was called, the variable used in it was not declared:\n{}".format(
                                    str(identifier_token)
                                ))

    def __check_function_call_catch_func_identifiers(self, identifier_token: Token, func_name: str) -> None:
        current_function_identifiers_to_catch = self.function_identifiers_to_catch_in_function.get(func_name)
        if current_function_identifiers_to_catch:
            current_function_identifiers_to_catch = self.function_identifiers_to_catch_in_function.get(func_name).copy()
        else:
            return None
        for func_name in current_function_identifiers_to_catch:
            if func_name not in self.known_identifiers:
                raise SemanticError(identifier_token,
                                    "Semantic Error\nWhen the function was called, the function name used in it was not declared:\n{}".format(
                                        str(identifier_token)
                                    )
                                    )

    def __check_identifiers(self) -> None:
        for node in self.tree.subtrees():
            if not node.parent():
                continue
            elif node.label() == '<Identifier>':
                current_node_parent_label = node.parent().label()
                if current_node_parent_label == '<assignment>' or current_node_parent_label == '<for_loop>':
                    self.known_identifiers.setdefault(self.__get_current_context(node), set()).add(
                        str(node.leaves()[0]))
                elif current_node_parent_label == '<function>':
                    if str(node.leaves()[0]) in self.known_identifiers:
                        self.identifiers_to_catch_in_function[str(node.leaves()[0])] = {str(node.leaves()[0])}
                    self.known_identifiers[str(node.leaves()[0])] = {str(node.leaves()[0])}
                    self.known_identifiers['<program>'].add(str(node.leaves()[0]))
                    self.__store_function_parameters(node)
                elif current_node_parent_label == '<Identifiers>':
                    self.known_identifiers[self.__get_current_context(node)].add(str(node.leaves()[0]))
                elif current_node_parent_label == '<function_call>':
                    if self.__get_current_context(node) != '<program>':
                        self.function_identifiers_to_catch_in_function.setdefault(self.__get_current_context(node),
                                                                                  set())
                        self.function_identifiers_to_catch_in_function[
                            self.__get_current_context(node)
                        ].add(str(node.leaves()[0]))
                        continue
                    if str(node.leaves()[0]) not in self.known_identifiers:
                        if str(node.leaves()[0]) in self.known_identifiers.get(self.__get_current_context(node)):
                            continue
                        raise SemanticError(
                            node.leaves()[0].token,
                            'Semantic Error\nThe function identifier was used before it was announced:\n{}'.format(
                                str(node.leaves()[0].token)
                            ))
                    if self.__get_current_context(node) == '<program>':
                        self.__check_function_call_catch_identifiers(node.leaves()[0].token, str(node.leaves()[0]))
                        self.__check_function_call_catch_func_identifiers(node.leaves()[0].token, str(node.leaves()[0]))
                    self.__check_function_parameters(node.parent())
                else:
                    current_context = self.__get_current_context(node)
                    if current_context != '<program>':
                        self.identifiers_to_catch_in_function.setdefault(current_context, set())
                        self.identifiers_to_catch_in_function[current_context].add(str(node.leaves()[0]))
                        continue
                    current_context = self.known_identifiers.get(self.__get_current_context(node))
                    if ((not current_context or
                         str(node.leaves()[0]) not in current_context) and
                            str(node.leaves()[0]) not in self.known_identifiers['<program>']):
                        raise SemanticError(
                            node.leaves()[0].token,
                            'Semantic Error\nThe identifier was encountered before it was announced:\n{}'.format(
                                str(node.leaves()[0].token)
                            )
                        )
