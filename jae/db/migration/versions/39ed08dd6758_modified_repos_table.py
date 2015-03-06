"""modified repos table

Revision ID: 39ed08dd6758
Revises: 2ed10d656484
Create Date: 2015-02-27 22:34:57.533899

"""

# revision identifiers, used by Alembic.
revision = '39ed08dd6758'
down_revision = '2ed10d656484'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean


def upgrade():
    op.add_column("repos",
                  Column("path", String(500)))
    op.add_column("repos",
                  Column("java", Boolean, default=False))

def downgrade():
    pass
