"""seed database

Revision ID: fc6d0ca5630c
Revises: 
Create Date: 2024-05-02 12:16:04.117089

"""

from ptmd.boot import initialize
from ptmd.config import Base, engine


# revision identifiers, used by Alembic.
revision = 'fc6d0ca5630c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    initialize()


def downgrade() -> None:
    Base.metadata.drop_all(engine)
