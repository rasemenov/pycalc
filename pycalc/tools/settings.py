"""
Stores global variables with mathematical rules for calculator.
Convenient to work with.
"""

import operator as op


OPEN_SEQ = ['(', '[', '{']
CLOSE_SEQ = [')', ']', '}']
MATH_OPERATORS = ['+', '-', '*', '/', '^', '%', '//', '**', '<', '<=', '==',
                  '!=', '>=', '>', '=', '!']
MATH_MAP = dict(zip(MATH_OPERATORS, ((op.add, 10), (op.sub, 10), (op.mul, 15),
                                     (op.truediv, 15), (op.pow, 20),
                                     (op.mod, 15), (op.floordiv, 15),
                                     (op.pow, 20), (op.lt, 5), (op.le, 5),
                                     (op.eq, 5), (op.ne, 5), (op.ge, 5),
                                     (op.gt, 5))))
TOTAL_LIST = OPEN_SEQ + CLOSE_SEQ + MATH_OPERATORS
