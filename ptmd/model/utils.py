""" This module contains utility functions for the harvester model.

@author: Terazus (D. Batista)
"""


def get_field_name(obj, field_name):
    """ Returns the field name of the model.

    @param obj: The object itself.
    @param field_name: The field name to be returned.

    @return: The field name of the model i the format: className.fieldName
    """
    return obj.__class__.__name__ + '.' + field_name
