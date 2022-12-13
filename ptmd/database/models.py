from datetime import timedelta

from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token
from flask import jsonify, Response
from sqlalchemy.orm import session as sqlsession

from .config import Base, db


class Organisation(Base):
    """ Organisation model. """
    __tablename__ = 'organisation'
    organisation_id = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False, unique=True)
    gdrive_id: str = db.Column(db.String(100), nullable=True, unique=True)

    def __iter__(self) -> dict:
        organisation = {
            'organisation_id': self.organisation_id,
            'name': self.name,
            'gdrive_id': self.gdrive_id if self.gdrive_id else None
        }
        for key, value in organisation.items():
            yield key, value


class User(Base):
    """ User model. """
    __tablename__: str = "user"
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password: str = db.Column(db.String(300), nullable=False)

    organisation_id: int = db.Column(db.Integer, db.ForeignKey('organisation.organisation_id'), nullable=True)
    organisation: db.relationship = db.relationship('Organisation', backref=db.backref('users'))

    def __init__(self, username: str, password: str, organisation: Organisation or None = None) -> None:
        self.username: str = username
        self.password: str = bcrypt.hash(password)
        if organisation and not isinstance(organisation, Organisation):
            raise TypeError('organisation must be an Organisation object')
        self.organisation: Organisation or None = organisation if organisation else None

    def __iter__(self) -> dict:
        user = {
            "id": self.id,
            "username": self.username,
            "organisation": dict(self.organisation) if self.organisation else None
        }
        for key, value in user.items():
            yield key, value

    def validate_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password)

    def change_password(self, old_password: str, new_password: str, session: sqlsession) -> bool:
        if self.validate_password(old_password):
            self.password = bcrypt.hash(new_password)
            session.commit()
            return True
        return False


def login_user(username: str, password: str, session: sqlsession) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    @param username
    @param password
    @param session: the database session
    @return: Response, int: the response message and the response code
    """
    user = session.query(User).filter_by(username=username).first()
    user = dict(user) if user and user.validate_password(password) else None
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=user['id'], expires_delta=timedelta(days=1000000))
    return jsonify(access_token=access_token), 200
