""" This module contains the user database model.
"""
from __future__ import annotations
from typing import Generator
from re import match

from passlib.hash import bcrypt
from ptmd.config import Base, db, session
from ptmd.const import ROLES
from ptmd.exceptions import PasswordPolicyError
from ptmd.database.const import PASSWORD_POLICY
from ptmd.database.models.token import Token
from ptmd.lib.email import send_validation_mail, send_validated_account_mail


class User(Base):
    """ User creator.

    :param username: the username
    :param password: the password
    :param email: the user email
    :param organisation_id: the organisation id the user belongs to
    """
    __tablename__: str = "user"
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password: str = db.Column(db.String(300), nullable=False)
    role: str = db.Column(db.String(80), nullable=False, default='disabled')
    email: str = db.Column(db.String(80), nullable=False, unique=True)

    organisation_id: int | None = db.Column(db.Integer, db.ForeignKey('organisation.organisation_id'), nullable=True)
    organisation = db.relationship('Organisation', backref=db.backref('users'))

    activation_token_id: int | None = db.Column(db.Integer, db.ForeignKey('token.token_id'), nullable=True)
    activation_token = db.relationship(
        'Token', backref=db.backref('user_activation'), foreign_keys=[activation_token_id]
    )
    reset_token_id: int | None = db.Column(db.Integer, db.ForeignKey('token.token_id'), nullable=True)
    reset_token = db.relationship('Token', backref=db.backref('user_reset'), foreign_keys=[reset_token_id])

    def __init__(
            self,
            username: str,
            password: str,
            email: str,
            role: str = 'disabled',
            organisation_id: int | None = None
    ) -> None:
        """ Constructor for the User class. Let's use encode the password with bcrypt before committing it to the
        database. """
        if not match(PASSWORD_POLICY, password):
            raise PasswordPolicyError
        self.username = username
        self.password = bcrypt.hash(password)
        self.email = email
        self.role = role
        self.organisation_id = organisation_id
        if role != 'admin':
            self.activation_token = Token(token_type='activation', user=self)

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        user_files: list[dict] = [dict(file) for file in self.files]
        if self.organisation:
            for file in [dict(file) for file in self.organisation.files]:
                if file not in user_files:
                    user_files.append(file)
        user: dict = {
            "id": self.id,
            "username": self.username,
            "organisation": self.organisation.name if self.organisation else None,
            "files": user_files,
            "role": self.role
        }
        for key, value in user.items():
            yield key, value

    def validate_password(self, password: str) -> bool:
        """ Checks if a user password is valid

        :param password: the password to check
        :return: True if the password is valid, False otherwise
        """
        return bcrypt.verify(password, self.password)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """ Change the user password.

        :param old_password: the old password
        :param new_password: the new password
        :return: True if the password was changed, False otherwise
        """
        if self.validate_password(old_password):
            self.set_password(new_password)
            return True
        return False

    def set_password(self, password: str) -> None:
        """ Set the user password. Helper function to avoid code repetition.

        :param password: the new password

        :raises PasswordPolicyError: if the password does not match the password policy
        """
        if not match(PASSWORD_POLICY, password):
            raise PasswordPolicyError
        self.password = bcrypt.hash(password)
        session.commit()

    def set_role(self, role: str) -> None:
        """ Set the user role. Helper function to avoid code repetition.
        """
        if role not in ROLES:
            raise ValueError(f"Invalid role: {role}")
        if role == 'banned':
            self.role = role
        else:
            {'enabled': self.__enable_account, 'user': self.__activate_account, 'admin': self.__make_admin}[role]()
        session.commit()

    def __enable_account(self) -> None:
        """ Changed the role to 'enabled' when the user confirms the email.
        """
        self.role = 'enabled'
        if self.activation_token:
            session.delete(self.activation_token)  # type: ignore
        send_validation_mail(self)

    def __activate_account(self) -> None:
        """ Change the role to 'user' when an admin activates an enabled account.
        """
        self.role = 'user'
        send_validated_account_mail(username=self.username, email=self.email)

    def __make_admin(self) -> None:
        """ Change the role to 'admin'.
        """
        self.role = 'admin'
