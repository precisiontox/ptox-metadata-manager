""" This module contains exception classes with custom messages used by the harvester to validate inputs

@author: Terazus (D. Batista)
"""


class InputTypeError(TypeError):
    """ Raised when a field is not of the expected type """
    def __init__(self, expected_type, actual_value, field_name):
        """ Constructor for the InputTypeError class

        :param expected_type: The expected type of the field
        :param actual_value: The actual value of the field
        :param field_name: The name of the field
        """
        self.expected_type = expected_type
        self.actual_value = actual_value
        self.message = "%s must be a %s but got %s with value %s" % (field_name, expected_type.__name__,
                                                                     type(actual_value).__name__, actual_value)
        super().__init__(self.message)


class InputValueError(ValueError):
    """ Raised when a field is not of the expected value """
    def __init__(self, expected_value, actual_value, field_name):
        """ Constructor for the InputValueError class

        :param expected_value: The expected value of the input
        :param actual_value: The actual value of the input
        :param field_name: The name of the field
        """
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.message = "%s must be one of %s but got %s" % (field_name, expected_value, actual_value)
        super().__init__(self.message)


class InputMinError(ValueError):
    """ Raised when a field is lower than the expected minimum value """
    def __init__(self, minimum, actual_value, field_name):
        """ Constructor for the InputMinError class

        :param minimum: The minimum value of the input
        :param actual_value: The actual value of the input
        :param field_name: The name of the field
        """
        self.minimum = minimum
        self.actual_value = actual_value
        self.message = "%s must be greater than %s but got %s" % (field_name, minimum, actual_value)
        super().__init__(self.message)


class InputRangeError(ValueError):
    """ Raised when a field is not within the expected range """
    def __init__(self, range_, actual_value, field_name):
        """ Constructor for the InputRangeError class

        :param range_: The range of the input (tuple with .min and .max)
        :param actual_value: The actual value of the input
        :param field_name: The name of the field
        """
        self.minimum = range_.min
        self.maximum = range_.max
        self.actual_value = actual_value
        self.message = "%s must be between %s and %s but got %s" % (field_name, range_.min, range_.max, actual_value)
        super().__init__(self.message)
