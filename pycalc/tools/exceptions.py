"""
This module defines base exception class for all exceptions used in
'pycalc' utility.
"""


class PyCalcBaseException(Exception):
    """
    Base exception subclassed from 'Exception'. Superclass for all
    exceptions of 'pycalc' module.
    Inside of library code various exceptions are handled but only
    this and its subclasses are allowed to propagate outside.
    """
    def __init__(self, message, expression=None):
        """
        Create standard message with 'ERROR' prefix.
        :param message: str(error message).
        :param expression: str(expression). Easy and uniformal formatting.
        """
        if expression is not None:
            message = ': '.join((message, f'"{expression}"'))
        self.message = 'ERROR: {}'.format(message)
        super().__init__(self.message)
