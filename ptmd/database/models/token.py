from datetime import datetime, timedelta
from secrets import token_hex

from ptmd.config import Base, db
from ptmd.lib.email import send_confirmation_mail


class Token(Base):
    """ A table to store tokens such as the email confirmation token and the password reset token.

    :param token_type: the type of the token
    :param user: the User the token belongs to
    """
    __tablename__: str = 'token'
    token_id: int = db.Column(db.Integer, primary_key=True)
    token: str = db.Column(db.String(300), nullable=False)
    token_type: str = db.Column(db.String(80), nullable=False)
    expires_on: datetime = db.Column(db.DateTime, nullable=False)

    def __init__(self, token_type: str, user: any) -> None:
        self.token = token_hex(16)
        self.token_type = token_type
        self.expires_on = datetime.now() + timedelta(days=1)
        send_confirmation_mail(username=user.username, email=user.email, token=self.token)
