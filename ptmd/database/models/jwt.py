from datetime import datetime, timezone

from ptmd.config import Base, db, session, jwt


class JWT(Base):
    """ Table storing valid and revoked JWTs """
    __tablename__ = 'jwt'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='jwt')

    def __init__(self, jti: str, user: Base):
        """A class to store JSON Web Tokens and identify valid tokens

        :param jti: the token identity decoded from the JWT
        :param user: the user to whom the JWT belongs

        Attributes:
            - jti: the JSON Token identity
            - created_at: the date the JWT was created
            - revoked: whether the JWT is revoked
            - user: the user to whom the JWT belongs
        """
        self.jti = jti
        self.user = user
        self.created_at = datetime.now(timezone.utc)


@jwt.token_in_blocklist_loader
def check_token_valid(jwt_header: dict, jwt_payload: dict) -> bool:
    """Check if a JWT is valid. Instead of a blocklist we create a whitelist that store all current valid JWTs.

    :param jwt_header: JWT header
    :param jwt_payload: JWT payload
    """
    return session.query(JWT.id).filter_by(jti=jwt_payload['jti']).scalar() is None  # type: ignore
