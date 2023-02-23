""" This module contains the user model.

@author: D. Batista (Terazus)
"""
from passlib.hash import bcrypt
from sqlalchemy.orm import session as sqlsession

from ptmd.config import Base, db
from .organisation import Organisation


class User(Base):
    """ User model.

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

    def __init__(self, username: str, password: str,
                 organisation: Organisation | None = None,
                 session: sqlsession = None) -> None:
        """ Constructor for the User class. Let's use encode the password with bcrypt before committing it to the
        database. """
        self.username: str = username
        self.password: str = bcrypt.hash(password)
        if organisation and not isinstance(organisation, Organisation) and not isinstance(organisation, str):
            raise TypeError('organisation must be an Organisation object or a string')
        if isinstance(organisation, Organisation):
            self.organisation: int = organisation
        elif organisation:
            if not session:
                raise ValueError('session must be provided if organisation is a string')
            org = session.query(Organisation).filter_by(name=organisation).first()
            self.organisation: Organisation = org

    def __iter__(self) -> dict:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        user = {
            "id": self.id,
            "username": self.username,
            "organisation": dict(self.organisation) if self.organisation else None
        }
        for key, value in user.items():
            yield key, value

    def validate_password(self, password: str) -> bool:
        """ Checks if a user password is valid

        :param password: the password to check
        :return: True if the password is valid, False otherwise
        """
        return bcrypt.verify(password, self.password)

    def change_password(self, old_password: str, new_password: str, session: sqlsession) -> bool:
        """ Change the user password.

        :param old_password: the old password
        :param new_password: the new password
        :param session: the database session
        :return: True if the password was changed, False otherwise
        """
        if self.validate_password(old_password):
            self.password = bcrypt.hash(new_password)
            session.commit()
            return True
        return False
