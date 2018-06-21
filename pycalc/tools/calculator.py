"""
Module contains tools for calculations of previously parsed expression strings.
Contains classes:
- ExpressionCalculator;
"""
import string
from importlib import import_module
import pycalc.tools.settings as rules
from pycalc.tools.utils import sorting_function
from pycalc.tools.exceptions import PyCalcBaseException


class ExpressionCalculator:
    """
    This class manages conversion of list of strings from parsed expression
    to Python objects, creation of right mathematical structure for expression
    and expression calculation.
    """
    def __init__(self, exp_string, exp_list, custom_module=None):
        """
        Check 'exp_list' for possible errors using '_check_input' method. Use
        'math' and 'builtins' modules by default.
        :param exp_string: str(expression string as in command line for errors);
        :param exp_list: list of strings from 'ExpressionParser';
        :param custom_module: list of strings with names of custom modules;
        """
        self.exp_string = exp_string
        self.exp_list = self._check_input(exp_list)
        self.custom_module = custom_module
        standard_libs = ['math', 'builtins']
        if self.custom_module is None:
            self.custom_module = standard_libs
        else:
            self.custom_module.extend(standard_libs)
        self.func_stack = []
        self.calc_args = False

    def _check_input(self, exp_list):
        """
        Check if provided parsed expression list is empty or its last item is
        unbalanced math operator etc.
        :param exp_list: list with parsed expression.
        """
        if len(exp_list) == 0:
            raise PyCalcBaseException('Empty expression string was provided.')
        elif exp_list[-1] in rules.MATH_OPERATORS:
            raise PyCalcBaseException('pycalc bet its hat that you\'ve '
                                      'forgotten sth in the end',
                                      self.exp_string)
        elif len(exp_list) == 2:
            if any([op in exp_list for op in rules.MATH_OPERATORS]):
                msg = 'This operators deal with two values. Try to insert sth '\
                      'in here'
                raise PyCalcBaseException(msg, self.exp_string)
        elif isinstance(exp_list, tuple):
            raise PyCalcBaseException('Someone messed up with brackets',
                                      self.exp_string)
        return exp_list

    def explore_data(self, data):
        """
        Recursively pass through parsed expression converting strings to Python
        objects and calculate results at every recursion level.
        :param data: list with parsed expression as 'exp_list'.
        :return: int|float|complex results of expression calculations.
        """
        result_list = []
        operand = None
        for item in data:
            if isinstance(item, list):
                operand = self.explore_data(item)
                if len(result_list) > 0:
                    if result_list[-1] == 'func':
                        result_list.pop()
                        try:
                            if isinstance(operand, list):
                                operand = self.func_stack.pop()(*operand)
                            else:
                                operand = self.func_stack.pop()(operand)
                        except TypeError:
                            raise PyCalcBaseException('Your function have '
                                                      'another signature.')
            if operand is not None:
                self._append_result(result_list, operand)
                operand = None
            else:
                item = self._convert_operator(item)
                if item is not None:
                    self._append_result(result_list, item)
        return self.calculate_exp(result_list)

    @staticmethod
    def _append_result(result_list, item):
        """
        Auxiliary method to change value of list. Determine 'item' type and
        either append or extend 'result_list'. No copy of list created.
        Returns 'None'.
        :param result_list: list to change.
        :param item: list of number to add to 'result_list'.
        """
        if isinstance(item, list):
            result_list.extend(item)
        else:
            result_list.append(item)

    def _convert_number(self, num_string):
        """
        Convert string to 'float' or 'int'. Also prepares function arguments for
        processing.
        :param num_string: str(string representation of number of args).
        :return: int|float number or list of function args.
        """
        if ',' in num_string:
            args = num_string.split(',')
            args = [self._convert_operator(item) for item in args if item != '']
            if len(args) == 1:
                return ['args', args[0]]
            else:
                return self._insert_arg_key(args)
        elif '.' in num_string:
            return float(num_string)
        else:
            return int(num_string)

    @staticmethod
    def _insert_arg_key(array):
        """
        Insert 'args' keyword in arbitrarily long list of args for
        further processing.
        :param array: list of function arguments.
        :return: new formatted list.
        """
        result = ['args'] * (len(array) * 2 - 1)
        result[0::2] = array
        return result

    def _convert_operator(self, item):
        """
        Detect math operators and return functions for them, try to convert
        numbers and raise exceptions on errors, append imported functions to
        function list of class instance.
        :param item: str(string representation of Python object).
        :return: int|float|str with number or keyword.
        """
        item = item.strip()
        if item in rules.MATH_MAP:
            return rules.MATH_MAP[item]
        elif not any([sym in item for sym in string.ascii_letters]):
            try:
                return self._convert_number(item)
            except ValueError:
                msg = 'We have all reasons to suspect typo in '                \
                      'here'
                raise PyCalcBaseException(msg, self.exp_string)
        elif ',' not in item:
            item = self._import_functions(item)
            if callable(item):
                self.func_stack.append(item)
                return 'func'
            else:
                return item
        elif ',' in item:
            return self._convert_number(item)

    def _import_functions(self, item):
        """
        Import custom and base modules and search for requested name in them.
        Raise exception if name wasn't found in modules.
        :param item: str(Python object name).
        :return: attribute of module with requested name.
        """
        if isinstance(self.custom_module[0], str):
            self.custom_module = [import_module(lib) for lib in self.custom_module]
        for lib in self.custom_module:
            if item in vars(lib):
                return getattr(lib, item)
        raise PyCalcBaseException('Dubious variable found: "{}"'.format(item))

    @staticmethod
    def _enumerate_list(exp_list):
        """
        Created list of mathematical operators and sort them in the right order.
        During list creation attach do each operator its index in original
        expression list.
        :param exp_list: list with Python object from original expression.
        :return: sorted list with functions corresponding to math operators.
        """
        func_list = [item for item in enumerate(exp_list) if isinstance(item[1],
                                                                        tuple)]
        return sorted(func_list, key=sorting_function)

    def _calc_func_args(self, exp_list):
        """
        Calculate values of complex function arguments.
        :param exp_list: list with Python objects of arguments separated with
                         'args' keyword.
        :return: list with calculated arguments values.
        """
        self.calc_args = True
        args_exp = [list() for _ in range(exp_list.count('args') + 1)]
        counter = 0
        for item in exp_list:
            if item != 'args':
                args_exp[counter].append(item)
            else:
                counter += 1
        return [self.calculate_exp(item) for item in args_exp]

    def calculate_exp(self, exp_list):
        """
        Calculate list of Python objects with special format conventions.
        :param exp_list: list of Python objects (numbers, functions etc).
        :return: number or list of values.
        """
        if 'args' in exp_list:
            exp_list = self._calc_func_args(exp_list)
            self.calc_args = False
        else:
            while len(exp_list) != 1:
                func_list = self._enumerate_list(exp_list)
                try:
                    prev = func_list[0][0] - 1
                    follow = func_list[0][0] + 1
                    func = func_list[0][1][0]
                    exp_list[prev:follow+1] = [func(exp_list[prev], exp_list[follow])]
                except IndexError:
                    msg = 'Operand\'s missing in your ' \
                          'expression'
                    raise PyCalcBaseException(msg, self.exp_string)
        if isinstance(exp_list, list):
            if len(exp_list) == 1:
                return exp_list[0]
        return exp_list
