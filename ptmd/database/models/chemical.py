from ptmd.database.config import Base, db


class Chemical(Base):
    __tablename__: str = 'chemical'
    chemical_id: int = db.Column(db.Integer, primary_key=True)
    common_name: str = db.Column(db.String(100), nullable=False, unique=True)
    name_hash_id: str = db.Column(db.String(100), nullable=True)
    formula: str = db.Column(db.String(100), nullable=False)
    ptx_code: int = db.Column(db.Integer, nullable=True, unique=True)

    def __iter__(self) -> dict:
        chemical: dict = {
            'chemical_id': self.chemical_id,
            'common_name': self.common_name,
            'name_hash_id': self.name_hash_id,
            'formula': self.formula,
            'ptx_code': self.ptx_code if self.ptx_code else None
        }
        for key, value in chemical.items():
            yield key, value
