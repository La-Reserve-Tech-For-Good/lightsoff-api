"""Add PlaceReview model

Revision ID: 41bf75c9dfe7
Revises: bc44630705da
Create Date: 2022-10-26 11:30:32.138796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "41bf75c9dfe7"
down_revision = "bc44630705da"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "place_review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("google_place_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("do_it_for_me", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["google_place_id"],
            ["place.google_place_id"],
            name="place_review_place_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("place_review")
    # ### end Alembic commands ###
