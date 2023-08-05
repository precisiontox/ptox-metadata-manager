""" Utility functions for querying. Contains a decorator to check if the user is admin before executing the
decorated function.
"""
from __future__ import annotations
from functools import wraps
from typing import Callable

from flask_jwt_extended import get_current_user, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from ptmd.config import jwt
from ptmd.const import ROLES
from ptmd.database import User


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header: dict, jwt_data: dict) -> User | None:
    """ callback for fetching authenticated user from db

    :param _jwt_header: JWT header
    :param jwt_data: JWT data

    :return: User object
    """
    return User.query.filter(User.id == jwt_data["sub"]).first()


def check_role(role: str = "enabled") -> Callable:
    """ Decorator to check if the user is at least a user or admin before executing the decorated function

    :param role: minimum role required to execute the decorated function
    """
    def decorator(f):
        """ Decorator function """
        @wraps(f)
        def decorator_function(*args, **kwargs):
            """ wrapper logic """
            verify_jwt_in_request()
            current_user: User = get_current_user()
            allowed: bool = is_allowed(user_role=current_user.role, level=role)
            if not allowed:
                raise NoAuthorizationError("You are not authorized to access this route")
            return f(*args, **kwargs)
        return decorator_function
    return decorator


def is_allowed(user_role: str, level: str = 'enabled') -> bool:
    """ Checks if the user is allowed to access a given route.

    :param user_role: role of the user
    :param level: minimum role required to access the route

    :return: True if the user is allowed to access the route, False otherwise
    """
    if user_role == 'admin':
        return True
    if user_role == 'banned':
        return False
    if ROLES.index(user_role) >= ROLES.index(level):
        return True
    return False
