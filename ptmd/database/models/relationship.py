""" This module contains the relationships tables.
"""

from ptmd.config import Table, db, Base


files_doses = Table(
    "files_doses",
    Base.metadata,
    db.Column("file_id", db.ForeignKey("file.file_id"), primary_key=True),
    db.Column("dose_id", db.ForeignKey("dose.dose_id"), primary_key=True),
    comment="A Table that represents the relationship between files and doses."
)


files_chemicals = Table(
    "files_chemicals",
    Base.metadata,
    db.Column("file_id", db.ForeignKey("file.file_id"), primary_key=True),
    db.Column("chemical", db.ForeignKey("chemical.chemical_id"), primary_key=True),
    comment="A Table that represents the relationship between files and compounds."
)

files_timepoints = Table(
    "files_timepoints",
    Base.metadata,
    db.Column("file_id", db.ForeignKey("file.file_id"), primary_key=True),
    db.Column("timepoint_id", db.ForeignKey("timepoint.timepoint_id"), primary_key=True),
    comment="A Table that represents the relationship between files and timepoints."
)
