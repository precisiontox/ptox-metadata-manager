""" This module contains the relationships tables.

@author: D. Batista (Terazus)
"""

from ptmd.config import Table, db, Base


files_doses = Table(
    "files_doses",
    Base.metadata,
    db.Column("file_id", db.ForeignKey("file.file_id"), primary_key=True),
    db.Column("dose_id", db.ForeignKey("dose.dose_id"), primary_key=True),
    comment="A Table that represents the relationship between files and doses."
)
