"""
This module contains class with logic to parse string with mathematical
expression into list of strings and lists.
Contains classes:
- ExpressionParser;
"""
import pycalc.tools.settings as rules
from pycalc.tools.exceptions import PyCalcBaseException


class ExpressionParser:
    """
    Class with monster 'parse_input' method with all logic to obtain parsed
    expression in format suitable for further calculations.
    """
    def __init__(self):
        """
        Initialize private '_expression' attribute access to which controlled
        by properties. It's required only for error messages and controlled
        to avoid multiple assignments during recursion.
        """
        self._expression = None

    @property
    def expression(self):
        """
        Getter method for 'expression' instance attr.
        :return: value of '_expression'.
        """
        return self._expression

    @expression.setter
    def expression(self, value):
        """
        Set '_expression' attribute to 'value' if it wasn't already set.
        :param value: str(expression).
        """
        if self._expression is None:
            self._expression = value

    def parse_input(self, exp_string, parse_one=False):
        """
        Parse provided string into list of strings and lists recursively. Also
        allows 'peek ahead' of current position in string on some occasions.
        Pass symbol by symbol through the string and construct desired structure.
        Each opening bracket triggers new call to method and creates list
        inside current list.
        :param exp_string: str(string with expression).
        :param parse_one: boolean if True parse up to first math operator.
        :return: list of strings and lists.
        """
        self.expression = exp_string
        expression_stack = []
        exp_string = exp_string.strip()
        temp_str = ''
        number = 0
        for index, item in enumerate(exp_string):
            if parse_one and (item in rules.TOTAL_LIST):
                expression_stack.append(self._control_parsing(item,
                                                              temp_str))
                break
            # 'number' and 'index' used to jump forward after return from
            # upper recursion levels.
            if number != index:
                continue
            else:
                number += 1
            if item in rules.OPEN_SEQ:
                expression_stack.append(temp_str)
                if self._check_operators(expression_stack):
                    # Allow implicit multiplication between number and bracket.
                    if expression_stack[-1].isdigit():
                        expression_stack.append('*')
                temp_str = ''
                try:
                    res, number = self.parse_input(exp_string[(index + 1):])
                except ValueError:
                    # Recursive copy return unexpected values -> recursion
                    # is amiss -> brackets is awry.
                    raise PyCalcBaseException('Someone messed up with brackets',
                                              self.expression)
                number += index
                expression_stack.append(res)
            elif item in rules.CLOSE_SEQ:
                expression_stack.append(temp_str)
                return self._clean_spaces(expression_stack), index + 2
            elif item in rules.MATH_OPERATORS:
                expression_stack.append(temp_str)
                # Check what kind of operator it is.
                if len(exp_string) - index > 2 and \
                        exp_string[index + 1] in ['/', '*', '=']:
                    item += exp_string[index + 1]
                    number += 1
                    expression_stack.append(item)
                # Escape signs into lists with multiplication.
                elif index == 0:
                    result, dif = self._deal_with_sign(item,
                                                       exp_string[(index + 1):])
                    expression_stack.extend(result)
                    number += dif
                elif self._check_operators(expression_stack):
                    if self._clean_spaces(expression_stack)[-1] in \
                            rules.MATH_OPERATORS:
                        result, dif = self._deal_with_sign(item,
                                                           exp_string[(index+1):])
                        expression_stack.extend(result)
                        number += dif
                    else:
                        expression_stack.append(item)
                else:
                    expression_stack.append(item)
                temp_str = ''
            else:
                temp_str = temp_str + item
        else:
            expression_stack.append(temp_str)
        return self._clean_spaces(expression_stack)

    def _deal_with_sign(self, item, expression):
        """
        Escape signed numbers into lists with multiplication of signed 1 with
        unsigned number. Must work with brackets and functions.
        :param item: str(math sign).
        :param expression: str(rest of expression after sign).
        :return: list with escape sequence.
        """
        tmp_list = [item + '1', '*']
        res = self.parse_input(expression, True)
        if not res:
            return item, 0
        if res[0] == 'extra':
            return [tmp_list + ['1'], '*'], 0
        else:
            return [tmp_list + res], len(res[0]) + expression.index(res[0])

    @staticmethod
    def _control_parsing(item, temp_str):
        """
        Return specified values during signed number escaping  process.
        :param item: str(current symbol during 'parse_one'=True call).
        :param temp_str: str(already parsed symbols).
        :return: str item or 'extra' key.
        """
        if temp_str == '':
            return 'extra'
        elif temp_str.isalpha():
            if item in rules.OPEN_SEQ:
                return 'extra'
            else:
                return temp_str
        else:
            return temp_str

    def _check_operators(self, expression_stack):
        """
        Perform length check of list with results parsed so far. Also check if
        previous item is a list. Store widely used comparisons.
        :param expression_stack: list with parsed expression part.
        :return: boolean.
        """
        expression_stack = self._clean_spaces(expression_stack)
        if len(expression_stack) == 0:
            return False
        if isinstance(expression_stack[-1], list):
            return False
        return True

    @staticmethod
    def _clean_spaces(array):
        """
        Remove redundant empty strings from list with parsed results.
        :param array: list with parsed results.
        :return: cleared list without '' and ' '.
        """
        return [item for item in array if item not in ('', ' ')]
