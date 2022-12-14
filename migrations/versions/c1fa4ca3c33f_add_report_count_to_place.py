"""Add report_count to Place

Revision ID: c1fa4ca3c33f
Revises: e6c76ef765af
Create Date: 2022-10-27 14:37:46.244937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1fa4ca3c33f"
down_revision = "e6c76ef765af"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("place", sa.Column("report_count", sa.Integer()))
    op.execute("UPDATE place SET report_count = 1")
    op.execute("ALTER TABLE place ALTER COLUMN report_count SET NOT NULL")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("place", "report_count")
    # ### end Alembic commands ###
