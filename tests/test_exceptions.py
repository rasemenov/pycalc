"""
Module contains test cases for 'exceptions.py' module's unit tests.
Should be ran with 'unittest' module.
"""
import unittest
import pycalc.tools.exceptions as exc


class TestCalcExceptions(unittest.TestCase):
    """
    Serves as container for test cases devoted to 'PyCalcBaseException'
    tests.
    """
    def test_creation(self):
        """
        Verify correctness of exception instance attributes.
        """
        args = (['One'], ['One', 'long_expression'])
        res = ('ERROR: One', 'ERROR: One: "long_expression"')
        counter = 0
        for case in args:
            with self.subTest(case=case):
                err = exc.PyCalcBaseException(*case)
                self.assertEqual(err.message, res[counter])
                counter += 1
