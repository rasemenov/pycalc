"""
This module contains classes for 'ExpressionParser' unit testing.
Includes classes:
- TestParseInput;
- TestAuxMethods.
"""
import unittest
import unittest.mock as mock
from pycalc.tools.parser import ExpressionParser
from pycalc.tools.settings import MATH_OPERATORS
from pycalc.tools.exceptions import PyCalcBaseException


class TestParseInput(unittest.TestCase):
    """
    Test main logic concentrated in 'parse_input' method.
    """
    def setUp(self):
        """
        Assign instance of 'ExpressionParser' to 'parser' attribute for
        convenient usage.
        """
        self.parser = ExpressionParser()

    def tearDown(self):
        """
        Reset 'parser' attribute.
        """
        self.parser = None

    def test_separate_to_items(self):
        """
        For simple cases parser must create list of math symbols from
        expression string.
        """
        inp_expr = ('1{}1', '1 {} 1', '1{} 1', '1 {}1')
        for expr in inp_expr:
            for op in MATH_OPERATORS:
                with self.subTest(op=op):
                    res = self.parser.parse_input(expr.format(op))
                    self.assertEqual(['1', op, '1'],
                                     [num.strip() for num in res])

    def _simple_assertion(self, inp, expected):
        """
        Helper method to assert standard cases.
        :param inp: iterable with input strings for parser.
        :param expected: iterable with expected results to compare with.
        """
        for expr in range(len(inp)):
            with self.subTest(expr=expr):
                self.assertEqual(self.parser.parse_input(inp[expr]),
                                 expected[expr])

    def test_single_brackets(self):
        """
        Expressions in brackets trigger recursive call to the same method.
        """
        inp_expr = ('1.0+(1.0*1.0)', '1.0+1.0-(1.0//1.0)')
        result = (['1.0', '+', ['1.0', '*', '1.0']],
                  ['1.0', '+', '1.0', '-', ['1.0', '//', '1.0']])
        self._simple_assertion(inp_expr, result)

    def test_sign_sequence(self):
        """
        Parser converts sequences of '+' or '-' signs to mathematical
        multiplications of signed '1'.
        """
        inp_expr = ('+1', '-+1', '+-1')
        result = ([['+1', '*', '1']], [['-1', '*', '1'], '*', ['+1', '*', '1']],
                  [['+1', '*', '1'], '*', ['-1', '*', '1']])
        self._simple_assertion(inp_expr, result)

    def test_math_constants(self):
        """
        Verify that parser process mathematical constants in the right way.
        """
        inp_expr = ('e', 'pi', '-pi', 'tau', 'inf', 'nan')
        result = (['e'], ['pi'], [['-1', '*', 'pi']], ['tau'], ['inf'], ['nan'])
        self._simple_assertion(inp_expr, result)

    def test_functions(self):
        """
        After parsing function's definition must consist of func name and
        its arguments in the following list. Multiple function's arguments
        separated by commas must not be divided to separate strings.
        """
        inp_expr = ('sin(30)', 'pow(2, 3)', 'log(sin(30))',
                    'my_func(1, 2, 3, 4)')
        result = (['sin', ['30']], ['pow', ['2, 3']], ['log', ['sin', ['30']]],
                  ['my_func', ['1, 2, 3, 4']])
        self._simple_assertion(inp_expr, result)

    def test_sign_before_functions(self):
        """
        Ambiguous signs before function declarations must be separated from
        function names.
        """
        inp_expr = ('1+-sin(30)', '2**-abs(30)')
        result = (['1', '+', ['-1', '*', '1'], '*', 'sin', ['30']],
                  ['2', '**', ['-1', '*', '1'], '*', 'abs', ['30']])
        self._simple_assertion(inp_expr, result)

    def test_surprising_multiplication(self):
        """
        For some reason parser must support implicit multiplication between
        numbers and expressions in brackets and function.
        """
        inp_expr = ('3(2+1)', '5+1(1+1)', '5sin(2)')
        result = (['3', '*', ['2', '+', '1']],
                  ['5', '+', '1', '*', ['1', '+', '1']],
                  ['5sin', ['2']])
        self._simple_assertion(inp_expr, result)

    def test_error_recursion(self):
        """
        Parser process errors caused by brackets mismatch. Those mismatches
        may be recognized at deep recursion level. At this point original
        expression must be available for error message.
        """
        with self.assertRaises(PyCalcBaseException) as err:
            self.parser.parse_input('((((((1)+2)+3)+4)+5)')
        self.assertEqual(err.exception.message,
                         'ERROR: Someone messed up with brackets: '
                         '"((((((1)+2)+3)+4)+5)"')


class TestAuxMethods(unittest.TestCase):
    """
    Test cases for various auxiliary methods of 'ExpressionParser' class.
    """
    def setUp(self):
        """
        Recreate instance of 'ExpressionParser' for every test case.
        """
        self.parser = ExpressionParser()

    def tearDown(self):
        """
        Remove link to used instance of 'ExpressionParser' from 'parser' attr.
        """
        self.parser = None

    def test_deal_with_sign(self):
        """
        Test conditional control flow of 'deal_with_sign' method.
        Mock 'parse_input' method to control its output.
        """
        item = '-'
        expr = ['', ' 1.0+2', '1*(2)', 'sin']
        return_vals = [[], ['1.0'], ['1'], ['sin']]
        result = [('-', 0), ([['-1', '*', '1.0']], 4), ([['-1', '*', '1']], 1),
                  ([['-1', '*', 'sin']], 3)]
        control_mock = mock.Mock(side_effect=return_vals)
        self.parser.parse_input = control_mock
        for indx in range(len(expr)):
            with self.subTest(indx=indx):
                self.assertEqual(self.parser._deal_with_sign(item, expr[indx]),
                                 result[indx])
        # Method 'deal_with_sign' called each time 'deal_with_sign' is called.
        self.assertEqual(control_mock.call_count, len(expr))

    def test_control_parsing(self):
        """
        Verify that 'control_parsing' method works as expected.
        """
        temp_strs = ['', 'alpha', '3.0']
        items = ['3.0', '(']
        res = ['extra', 'alpha', '3.0', 'extra', 'extra', '3.0']
        indx = 0
        for item in items:
            for tmp in temp_strs:
                with self.subTest(item=item, tmp=tmp):
                    self.assertEqual(self.parser._control_parsing(item, tmp),
                                     res[indx])
                indx += 1

    def test_check_operators(self):
        """
        Assess correctness of boolean values returned by 'check_operator'
        method of 'ExpressionParser' class.
        """
        clean_mock = mock.Mock(side_effect=lambda value: value)
        self.parser._clean_spaces = clean_mock
        inp = [[], [[]], [1]]
        res = [False, False, True]
        for case in inp:
            with self.subTest(case=case):
                self.assertEqual(self.parser._check_operators(case),
                                 res[inp.index(case)])
        # 'clean_spaces' method triggered on each 'check_operator' call.
        self.assertEqual(clean_mock.call_count, len(inp))

    def test_clean_spaces(self):
        """
        Verify that 'clean_spaces' method removes redundant empty strings from
        list as designed.
        """
        array = [1, '', '1', ' ', '1 1', 1.0]
        res = [1, '1', '1 1', 1.0]
        self.assertEqual(self.parser._clean_spaces(array), res)
