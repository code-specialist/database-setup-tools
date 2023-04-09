"""create account table

Revision ID: 910ed4335d55
Revises:
Create Date: 2023-04-09 10:05:41.789277

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "910ed4335d55"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Unicode(200)),
    )


def downgrade() -> None:
    op.drop_table("account")
