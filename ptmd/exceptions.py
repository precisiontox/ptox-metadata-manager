class PasswordPolicyError(Exception):
    """ Exception raised when a password does not meet the password policy """

    def __init__(self) -> None:
        self.message = "Password must between 8 and 20 characters long, contain at least one uppercase letter, one " \
                       "lowercase letter, one number and one special character."

    def __str__(self):
        return self.message
