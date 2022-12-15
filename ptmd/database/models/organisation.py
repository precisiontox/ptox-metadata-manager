from ptmd.database.config import Base, db


class Organisation(Base):
    """ Organisation model. """
    __tablename__: str = 'organisation'
    organisation_id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False, unique=True)
    gdrive_id: str = db.Column(db.String(100), nullable=True, unique=True)

    def __iter__(self) -> dict:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        organisation: dict = {
            'organisation_id': self.organisation_id,
            'name': self.name,
            'gdrive_id': self.gdrive_id if self.gdrive_id else None
        }
        for key, value in organisation.items():
            yield key, value
