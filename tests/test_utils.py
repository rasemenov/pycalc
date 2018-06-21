"""
This module contains test cases for content of 'utils.py' module.
Uses 'unittest' as tests' manager.
"""
import unittest
import pycalc.tools.utils as utils


class TestUtils(unittest.TestCase):
    """
    Collection of test cases for 'utils.py' module's content.
    """
    def test_sorting_function(self):
        """
        Check that function outputs expected values during regular expression
        comparison and comparison of expressions with raising to power.
        """
        inp = ([1, ('pow', 20)], [10, ('add', 10)])
        res = (-21, -10)
        counter = 0
        for case in inp:
            with self.subTest(case=case):
                self.assertEqual(utils.sorting_function(case), res[counter])
                counter += 1
