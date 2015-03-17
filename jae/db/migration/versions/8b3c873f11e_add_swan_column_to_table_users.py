"""add swan column to table users

Revision ID: 8b3c873f11e
Revises: 5a064cb40402
Create Date: 2015-03-17 18:46:59.344399

"""

# revision identifiers, used by Alembic.
revision = '8b3c873f11e'
down_revision = '5a064cb40402'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("users",
                  sa.Column("swan", sa.Integer))


def downgrade():
    pass
