"""Add latitude/longitude properties to Place

Revision ID: 3c43978440d2
Revises: c1fa4ca3c33f
Create Date: 2022-10-31 15:01:44.897903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c43978440d2"
down_revision = "c1fa4ca3c33f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("place", sa.Column("latitude", sa.Float()))
    op.add_column("place", sa.Column("longitude", sa.Float()))

    op.execute("UPDATE place SET latitude = 0")
    op.execute("UPDATE place SET longitude = 0")

    op.execute("ALTER TABLE place ALTER COLUMN latitude SET NOT NULL")
    op.execute("ALTER TABLE place ALTER COLUMN longitude SET NOT NULL")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("place", "longitude")
    op.drop_column("place", "latitude")
    # ### end Alembic commands ###
