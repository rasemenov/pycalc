"""
Module manages library tools to provide command line interface for the
calculator. Intended to be called from command line.
Contains functions:
- parse_args;
- main;
"""
import argparse
from pycalc.tools.calculator import ExpressionCalculator
from pycalc.tools.parser import ExpressionParser
from pycalc.tools.exceptions import PyCalcBaseException


def parse_args(*args):
    """
    Parse command line arguments using 'argparse' module. Yep it must contain
    'expression' positional arg but it won't work with some expressions and if
    add '--' escape into command line args '--help' won't work. This solution
    is just as good.
    :param args: inserted to call from scripts.
    :return: tuple(argparse.Namespace with module names as attributes,
             list with expression string.
    """
    parser = argparse.ArgumentParser(description='Pure-python command-line '
                                                 'calculator.')
    parser.add_argument('-m', '--use-modules', dest='module', action='append',
                        help='Additional modules to use')
    args = parser.parse_known_args(*args)
    if len(args[1]) == 0:
        raise PyCalcBaseException('No expression was provided.')
    return args


def main(*args):
    """
    Orchestrate creation of 'ExpressionParser' and 'ExpressionCalculator'
    classes and pass created instances parsed arguments.
    Print results of expression. 
    :param args: inserted to call from scripts.
    """
    try:
        args = parse_args(*args)
        parser = ExpressionParser()
        calc = ExpressionCalculator(args[1][0], parser.parse_input(args[1][0]),
                                    args[0].module)
        print(calc.explore_data(calc.exp_list))
    except PyCalcBaseException as err:
        print(err)


if __name__ == '__main__':
    main()
