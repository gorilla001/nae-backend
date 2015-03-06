"""containers table add flags column

Revision ID: 100316d01c4d
Revises: 13e2c721a021
Create Date: 2015-03-06 23:35:38.714212

"""

# revision identifiers, used by Alembic.
revision = '100316d01c4d'
down_revision = '13e2c721a021'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("containers",  
                  sa.Column("flags", sa.String(500)))

def downgrade():
    op.drop_column("containers", "flags")
