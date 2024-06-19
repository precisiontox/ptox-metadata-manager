"""delete token blocklist table and create jwt table

Revision ID: ed8a4d3a91fe
Revises: fc6d0ca5630c
Create Date: 2024-05-02 12:18:15.848957

"""
from alembic import op
from sqlalchemy.exc import OperationalError

from ptmd.config import Base, engine
from ptmd.logger import LOGGER


# revision identifiers, used by Alembic.
revision = 'ed8a4d3a91fe'
down_revision = 'fc6d0ca5630c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        op.drop_table('token_blocklist')
        LOGGER.info('Table token_blocklist has been deleted successfully')
    except OperationalError:
        LOGGER.error('Table token_blocklist has already been deleted')


def downgrade() -> None:
    Base.metadata.create_all(engine)
