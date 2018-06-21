"""
This module contains functions intended to verify expected behaviour of the
'ExpressionCalculator' class.
"""
import unittest
import unittest.mock as mock
from pycalc.tools.calculator import ExpressionCalculator
from pycalc.tools.exceptions import PyCalcBaseException


class TestExpressionCalculator(unittest.TestCase):
    """
    Collection of test cases for 'ExpressionCalculator' functional testing.
    """
    def setUp(self):
        """
        Create instance and assign to instance attributes all values required
        during testing.
        """
        self.calc = ExpressionCalculator('1', ['1'])

    def tearDown(self):
        """
        Clear stored instance of 'ExpressionCalculator'.
        """
        self.calc = None

    @mock.patch.object(ExpressionCalculator, '_check_input')
    def test_creation(self, mock_check):
        """
        Verify that during class instance creation all cases are dealt with.
        """
        cases = [('1+1', ['1', '+', '1'], None), ('1', ['1'], ['string']),
                 ('2**2', ['2', '**', '2'], ['string', 'struct'])]
        modules = (['math', 'builtins'], ['string', 'math', 'builtins'],
                   ['string', 'struct', 'math', 'builtins'])
        mock_check.side_effect = lambda value: value
        counter = 0
        for case in cases:
            with self.subTest(case=case):
                calc = ExpressionCalculator(*case)
                self.assertEqual(calc.exp_string, cases[counter][0])
                self.assertEqual(calc.exp_list, cases[counter][1])
                self.assertEqual(calc.custom_module, modules[counter])
                self.assertEqual(calc.func_stack, [])
                self.assertEqual(calc.calc_args, False)
                mock_check.assert_called_with(cases[counter][1])
            counter += 1

    def test_check_input(self):
        exp_list = ([], ['**'], ['+'], ['1', '-'], ['==', '1'], (0,))
        for expression in exp_list:
            with self.subTest(expression=expression):
                with self.assertRaises(PyCalcBaseException) as err:
                    self.calc._check_input(expression)
                self.assertIn('ERROR:', err.exception.message)

    def test_explore_data_recursion(self):
        """
        Confirm correct processing of expressions in brackets.
        """
        expr = ['1', '+', [[['1']]]]
        mock_convert = mock.Mock(side_effect=[1, 'add', 1])
        mock_calc = mock.Mock(side_effect=lambda value: value)
        self.calc._convert_operator = mock_convert
        self.calc.calculate_exp = mock_calc
        self.assertEqual(self.calc.explore_data(expr), [1, 'add', 1])
        self.assertEqual(['1', '+', '1'],
                         [call[0][0] for call in mock_convert.call_args_list])
        self.assertEqual([[1], [1], [1], [1, 'add', 1]],
                         [call[0][0] for call in mock_calc.call_args_list])

    def test_explore_data_func(self):
        """
        Method relies on string keys to process functions in expressions.
        Assess correctness of functions' calculations.
        """
        mock_func = mock.Mock(side_effect=['two args', 'two args', 'one arg',
                                           'one arg'])
        inp = ([mock_func, ['arg1', 'arg2']],
               [mock_func, ['arg']])
        mock_convert = mock.Mock(side_effect=['func', 'arg1', 'arg2',
                                              'func', 'arg'])
        mock_calc = mock.Mock(side_effect=lambda value: value)
        self.calc._convert_operator = mock_convert
        self.calc.calculate_exp = mock_calc
        for case in inp:
            with self.subTest(case=case):
                self.calc.func_stack.append(case[0])
                self.assertEqual(self.calc.explore_data(case), [case[0]()])
                self.assertEqual(len(self.calc.func_stack), 0)
        self.assertEqual([call[0][0] for call in mock_convert.call_args_list],
                         [mock_func, 'arg1', 'arg2', mock_func, 'arg'])
        self.assertEqual([call[0][0] for call in mock_calc.call_args_list],
                         [['arg1', 'arg2'], ['two args'], ['arg'], ['one arg']])

    def test_explore_data_operand(self):
        """
        Results of calculations of expressions in brackets and function
        arguments may be both numeric values and lists.
        Both cases must be considered.
        """
        inp = ([['1'], '+', 'gcd', ['1,2']])
        mock_convert = mock.Mock(side_effect=[1, 'add', 'func', [1, 'args', 2]])
        mock_calc = mock.Mock(side_effect=lambda value: value)
        self.calc._convert_operator = mock_convert
        self.calc.calculate_exp = mock_calc
        self.calc.func_stack.append(lambda *value: value)
        self.assertEqual(self.calc.explore_data(inp),
                         [1, 'add', (1, 'args', 2)])

    def test_convert_number(self):
        """
        Method responsible for conversion from string to Python numeric types
        as well as creating formatted lists out of function arguments.
        """
        inp = ('1.0', '0.1', '.1', '1', '1,2', '1,')
        res = (1.0, 0.1, 0.1, 1, [1, 'args', 2], ['args', 1])
        mock_convert = mock.Mock(side_effect=(1, 2, 1))
        self.calc._convert_operator = mock_convert
        counter = 0
        for case in inp:
            with self.subTest(case=case):
                self.assertEqual(self.calc._convert_number(case),
                                 res[counter])
                counter += 1
        self.assertEqual([call[0][0] for call in mock_convert.call_args_list],
                         ['1', '2', '1'])

    @mock.patch('pycalc.tools.calculator.rules')
    def test_convert_operator(self, mock_rules):
        """
        Test correct processing of mathematical operators, function arguments,
        function definitions.
        """
        inp = ('+', '1', 'sin', 'mock', ',')
        mock_convert = mock.Mock(side_effect=[1, 'yep'])
        mock_import = mock.Mock(side_effect=[lambda: None, 'item'])
        mock_rules.MATH_MAP = {'+': 'add'}
        res = ['add', 1, 'func', 'item', 'yep']
        self.calc._convert_number = mock_convert
        self.calc._import_functions = mock_import
        counter = 0
        for case in inp:
            with self.subTest(case=case):
                self.assertEqual(self.calc._convert_operator(case),
                                 res[counter])
                counter += 1

    def test_convert_operator_exception(self):
        """
        Check if method raise the exception when invalid input is provided.
        """
        with self.assertRaises(PyCalcBaseException) as err:
            self.calc._convert_operator('1 2')
        self.assertIn('ERROR:', err.exception.message)

    @mock.patch('pycalc.tools.calculator.import_module')
    def test_import_functions(self, mock_import):
        """
        Import functions must import modules at first call and search in
        imported modules for subsequent calls. Also verify that exception is
        raised when search failed.
        """
        mock_module = mock.Mock(foo='spam')
        empty_mock = mock.Mock(side_effect=KeyError)
        mock_import.side_effect = [empty_mock, empty_mock, mock_module]
        calc = ExpressionCalculator('1', ['1'], ['module'])
        self.assertEqual(calc.custom_module, ['module', 'math', 'builtins'])
        self.assertEqual(calc._import_functions('foo'), 'spam')
        self.assertEqual(calc.custom_module,
                         [empty_mock, empty_mock, mock_module])
        with self.assertRaises(PyCalcBaseException) as err:
            calc._import_functions('food')
        self.assertIn('ERROR:', err.exception.message)

    @mock.patch('pycalc.tools.calculator.sorting_function')
    def test_enumerate_list(self, mock_sort):
        """
        Correct work of 'enumerate_list' method crucial for calculations.
        Check output format and calls to sorting function.
        """
        # Simple sort according to operator priority
        mock_sort.side_effect = lambda val: -val[1][1]
        inp = [1, ('add', 1), 2, ('pow', 5), 10]
        result = self.calc._enumerate_list(inp)
        self.assertEqual(result, [(3, ('pow', 5)), (1, ('add', 1))])
        self.assertEqual(mock_sort.call_count, 2)

    def test_calc_func_args(self):
        """
        Test that method creates list with right number of function arguments,
        call expected methods and return result in required format.
        Also verify that 'calc_args' 'semaphore' of 'ExpressionCalculator'
        instance assigned right value on method entrance.
        """
        inp = ([1, 'args', [2, 2]], [1, 'args', 2, 'args', 3, 'args', 4])
        mock_calc = mock.Mock(side_effect=lambda value: value[0])
        self.calc.calculate_exp = mock_calc
        res = ([1, [2, 2]], [1, 2, 3, 4])
        counter = 0
        for item in inp:
            with self.subTest(item=item):
                self.assertEqual(self.calc._calc_func_args(item), res[counter])
                counter += 1
        self.assertEqual([call[0][0] for call in mock_calc.call_args_list],
                         [[1], [[2, 2]], [1], [2], [3], [4]])
        self.assertTrue(self.calc.calc_args)

    def test_calculate_exp_args(self):
        """
        Verify logical flow of the part dealing with calculations of functional
        arguments.
        Assert right changes to the 'calc_args' instance 'semaphore'.
        """
        inp = ([1, 'args', [2, 2]], [1, 'args', 2, 'args', 3])
        res = ([1, [2, 2]], [1, 2, 3])
        mock_calc = mock.Mock(side_effect=lambda value: list(filter(
                                            lambda val: val != 'args', value)))
        self.calc._calc_func_args = mock_calc
        counter = 0
        for case in inp:
            with self.subTest(case=case):
                self.assertFalse(self.calc.calc_args)
                self.assertEqual(self.calc.calculate_exp(case), res[counter])
                counter += 1

    def test_calculate_exp(self):
        """
        Check that method correctly interprets expression and handle exceptions.
        """
        func1 = mock.Mock(side_effect=lambda first, second: first + second)
        func2 = mock.Mock(side_effect=lambda this, other: this * other)
        inp = ([1, 'func1', 2], [1, 'func1', 2, 'func2', 3], [1, 'func1', 2])
        mock_enum = mock.Mock(side_effect=([(1, (func1, 1))],
                                           [(3, (func2, 2)), (1, (func1, 1))],
                                           [(1, (func1, 1))]))
        self.calc._enumerate_list = mock_enum
        res = (3, 7)
        for indx in range(len(inp) - 2):
            with self.subTest(indx=indx):
                self.assertEqual(self.calc.calculate_exp(inp[indx]), res[indx])
        with self.assertRaises(PyCalcBaseException) as err:
            self.calc.calculate_exp(inp[2])
        self.assertIn('ERROR:', err.exception.message)
