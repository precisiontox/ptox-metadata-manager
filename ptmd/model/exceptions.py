class InputTypeError(TypeError):
    def __init__(self, expected_type, actual_value, field_name):
        self.expected_type = expected_type
        self.actual_value = actual_value
        self.message = "%s must be a %s but got %s with value %s" % (field_name, expected_type.__name__,
                                                                     type(actual_value).__name__, actual_value)
        super().__init__(self.message)


class InputValueError(ValueError):
    def __init__(self, expected_value, actual_value, field_name):
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.message = "%s must be one of %s but got %s" % (field_name, expected_value, actual_value)
        super().__init__(self.message)


class InputMinError(ValueError):
    def __init__(self, minimum, actual_value, field_name):
        self.minimum = minimum
        self.actual_value = actual_value
        self.message = "%s must be greater than %s but got %s" % (field_name, minimum, actual_value)
        super().__init__(self.message)


class InputRangeError(ValueError):
    def __init__(self, range_, actual_value, field_name):
        self.minimum = range_.min
        self.maximum = range_.max
        self.actual_value = actual_value
        self.message = "%s must be between %s and %s but got %s" % (field_name, range_.min, range_.max, actual_value)
        super().__init__(self.message)
