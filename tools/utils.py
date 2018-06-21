"""
This module consists of auxiliary tools for main calculator modules.
Includes functions:
- sorting_function;
"""
import pycalc.tools.settings as rules


def sorting_function(exp_block):
    """
    Intended to sort mathematical operators by their priority in descending
    order. Passed as argument to 'sorted' function.
    :param exp_block: tuple(<index in list>, tuple(<function>, <priority>).
    :return: function priority with reversed sign. If function is 'pow' take
             its position in list in account.
    """
    if exp_block[1][1] == rules.MATH_MAP['**'][1]:
        return -exp_block[1][1] - exp_block[0]
    else:
        return -exp_block[1][1]
