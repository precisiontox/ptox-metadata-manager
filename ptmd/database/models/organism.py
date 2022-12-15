from ptmd.database.config import Base, db


class Organism(Base):
    __tablename__: str = 'organism'
    organism_id: int = db.Column(db.Integer, primary_key=True)
    ptox_biosystem_name: str = db.Column(db.String(100), nullable=False, unique=True)
    scientific_name: str = db.Column(db.String(100), nullable=False)

    def __iter__(self) -> dict:
        organism: dict = {
            'organism_id': self.organism_id,
            'scientific_name': self.scientific_name,
            'ptox_biosystem_name': self.ptox_biosystem_name
        }
        for key, value in organism.items():
            yield key, value
