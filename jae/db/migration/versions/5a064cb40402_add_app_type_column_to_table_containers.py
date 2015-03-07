"""add app_type column to table containers

Revision ID: 5a064cb40402
Revises: 100316d01c4d
Create Date: 2015-03-07 22:58:46.994244

"""

# revision identifiers, used by Alembic.
revision = '5a064cb40402'
down_revision = '100316d01c4d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("containers",
                 sa.Column("app_type", sa.String(10)))

def downgrade():
    pass
