""" This module contains utility functions for the database. In particular, a wrapper for getting the current user
without raising a runtime error when running scripts that don't rely on the API.
"""


from __future__ import annotations

from flask_jwt_extended import get_current_user as current_user

from ptmd.database.models.user import User


def get_current_user() -> User | None:
    """ Return the current user or None. Prevents runtime errors when running scripts that don't rely on the API.

    :return: The current user or None.
    """
    try:
        return current_user()
    except RuntimeError:
        return None
