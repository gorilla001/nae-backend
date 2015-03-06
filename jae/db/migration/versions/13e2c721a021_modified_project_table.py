"""modified project table

Revision ID: 13e2c721a021
Revises: 39ed08dd6758
Create Date: 2015-02-28 00:13:36.663900

"""

# revision identifiers, used by Alembic.
revision = '13e2c721a021'
down_revision = '39ed08dd6758'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    #op.alter_column("projects", "name", nullable=False) 
    op.create_unique_constraint(None, "projects", ["name"])


def downgrade():
    pass
