"""add image_link column to protected assets"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "202410090002"
down_revision = "202410090001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "protected_assets",
        sa.Column("image_link", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("protected_assets", "image_link")
