""" This module contains the user creator.

@author: D. Batista (Terazus)
"""
from __future__ import annotations
from typing import Generator

from passlib.hash import bcrypt

from ptmd.config import Base, db, session
from ptmd.database.models import Organisation


class User(Base):
    """ User creator.

    :param username: the username
    :param password: the password
    :param organisation: the organisation the user belongs to (either an Organisation object or a string pointing to the
    organisation name)
    """
    __tablename__: str = "user"
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password: str = db.Column(db.String(300), nullable=False)

    organisation_id: int = db.Column(db.Integer, db.ForeignKey('organisation.organisation_id'), nullable=True)
    organisation = db.relationship('Organisation', backref=db.backref('users'), lazy='subquery')

    def __init__(self, username: str, password: str, organisation: Organisation | None | str = None) -> None:
        """ Constructor for the User class. Let's use encode the password with bcrypt before committing it to the
        database. """
        self.username: str = username
        self.password: str = bcrypt.hash(password)
        if organisation and not isinstance(organisation, (Organisation, str)):
            raise TypeError('organisation must be an Organisation object or a string')
        if isinstance(organisation, Organisation):
            self.organisation = organisation
        elif organisation:
            org = Organisation.query.filter(Organisation.name == organisation).first()
            self.organisation = org

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        user = {
            "id": self.id,
            "username": self.username,
            "organisation": self.organisation.organisation_id if self.organisation else None,
            "files": [dict(file) for file in self.files]
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
            self.password = bcrypt.hash(new_password)
            session.commit()
            return True
        return False
