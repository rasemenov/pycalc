"""
Provide test cases for 'main.py' module testing. Should be ran by 'unittest'.
"""
import unittest
import unittest.mock as mock
import argparse
import sys
from io import StringIO
from pycalc.main import parse_args, main
from pycalc.tools.exceptions import PyCalcBaseException


class TestMain(unittest.TestCase):
    """
    Collection of test cases for 'main.py' functions.
    """
    def setUp(self):
        """
        Stream prints to buffer.
        """
        self.out_back = sys.stdout
        self.buffer = StringIO()
        sys.stdout = self.buffer

    def tearDown(self):
        """
        Restore original stdout stream.
        """
        sys.stdout = self.out_back

    def test_parse_args(self):
        """
        Verify that function returns tuple with 'argparse.Namespace' and list
        with expression string.
        """
        inp = '1+1'
        result = parse_args([inp])
        self.assertIsInstance(result[0], argparse.Namespace)
        self.assertIs(result[0].module, None)
        self.assertEqual(result[1], ['1+1'])

    def test_parse_args_exception(self):
        """
        Check if function raises exception on empty input.
        """
        with self.assertRaises(PyCalcBaseException) as err:
            parse_args([])
        self.assertIn('ERROR:', err.exception.message)

    @mock.patch('pycalc.main.ExpressionCalculator')
    @mock.patch('pycalc.main.ExpressionParser')
    def test_main(self, mock_parser, mock_calc):
        """
        Test that instancec of appropriate classes created and required
        methods called.
        """
        parse_input = mock.Mock(side_effect=[['1']])
        mock_parser.return_value = mock.Mock(parse_input=parse_input)
        explore_data = mock.Mock(side_effect=[1])
        mock_calc.return_value = mock.Mock(explore_data=explore_data)
        main(['1'])
        self.assertEqual('1', self.buffer.getvalue().strip())

    @mock.patch('pycalc.main.ExpressionParser')
    def test_main_exception(self, mock_parser):
        """
        Check that function handles exceptions.
        """
        mock_parser.side_effect = PyCalcBaseException('oops')
        with self.assertRaises(PyCalcBaseException) as err:
            main(['1'])
        self.assertEqual('ERROR: oops', err.exception.message)
