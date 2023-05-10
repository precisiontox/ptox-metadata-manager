from ptmd.config import Base, db, jwt, session


class TokenBlocklist(Base):
    """ Token block list required to log-out users
    """
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)


# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    return session.query(TokenBlocklist.id).filter_by(jti=jwt_payload["jti"]).scalar() is not None
