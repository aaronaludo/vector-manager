"""${message}"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
% if upgrades:
${upgrades}
% else:
    pass
% endif


def downgrade() -> None:
% if downgrades:
${downgrades}
% else:
    pass
% endif
