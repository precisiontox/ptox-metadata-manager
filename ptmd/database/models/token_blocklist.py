""" Token block list model used to store expired JWT
"""
from datetime import datetime, timezone

from ptmd.config import Base, db, jwt, session


class TokenBlocklist(Base):
    """ Token block list required to log-out users
    """
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti: str):
        """ Create a new token block list entry """
        self.jti = jti
        self.created_at = datetime.now(timezone.utc)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    """ Check if a JWT exists in the database blocklist

    @param jwt_header: JWT header
    @param jwt_payload: JWT payload
    """
    return session.query(TokenBlocklist.id).filter_by(jti=jwt_payload["jti"]).scalar() is not None
