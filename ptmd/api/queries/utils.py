""" Utility functions for querying. Contains a decorator to check if the user is admin before executing the
decorated function.

@author: D. Batista (Terazus)
"""
from __future__ import annotations
from functools import wraps
from typing import Callable

from flask_jwt_extended import get_current_user, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from ptmd.config import jwt
from ptmd.database import User


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    """ callback for fetching authenticated user from db

    :param _jwt_header: JWT header
    :param jwt_data: JWT data

    :return: User object
    """
    return User.query.filter(User.id == jwt_data["sub"]).first()


def check_admin_only() -> Callable:
    """ Decorator to check if the user is admin before executing the decorated function """
    def decorator(f):
        """ Decorator function """
        @wraps(f)
        def decorator_function(*args, **kwargs):
            """ wrapper logic """
            verify_jwt_in_request()
            current_user = get_current_user()
            if not current_user or current_user.username != "admin":
                raise NoAuthorizationError("You are not authorized to create a new user")
            return f(*args, **kwargs)
        return decorator_function
    return decorator


def validate_inputs(inputs: list, data: dict) -> tuple[bool, str | dict]:
    """ Check if all the inputs are in the data dictionary

    :param inputs: list of inputs
    :param data: dictionary containing the inputs

    :return: tuple containing a boolean and a string or a dictionary. If the boolean is True, the dictionary
    contains the inputs. If the boolean is False, the string contains the missing input.
    """
    user_inputs = {}
    if data:
        for value in inputs:
            if value not in data:
                return False, value
            user_inputs[value] = data[value]
    return True, user_inputs
