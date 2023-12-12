""" Custom exceptions for the ptmd package """
from __future__ import annotations
from abc import ABC


class APIError(Exception, ABC):
    """ Exception raised when an API error occurs. This is an abstract class, do not use directly. """

    def __init__(self) -> None:
        """ Constructor, do not use """
        self.message: str | None = None
        raise SyntaxError("Cannot instantiate abstract class APIError")

    def __str__(self) -> str:
        """ String representation of the exception """
        return self.message or ""


class PasswordPolicyError(APIError):
    """ Exception raised when a password does not meet the password policy """

    def __init__(self) -> None:
        """ Constructor """
        self.message: str = "Password must be between 8 and 20 characters long, contain at least one uppercase " \
                            "letter, one lowercase letter, one number and one special character."


class TokenExpiredError(APIError):
    """ Exception raised when a token is expired """

    def __init__(self) -> None:
        """ Constructor """
        self.message: str = "Token expired"


class TokenInvalidError(APIError):
    """ Exception raised when a token is invalid """

    def __init__(self) -> None:
        """ Constructor """
        self.message: str = "Invalid token"


class TimepointValueError(APIError):
    """ Exception raised when a timepoint value is invalid """

    def __init__(self) -> None:
        """ Constructor """
        self.message: str = "Timepoint value must be a positive integer"
