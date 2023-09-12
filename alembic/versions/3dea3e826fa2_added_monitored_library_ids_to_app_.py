"""added monitored library ids to app config

Revision ID: 3dea3e826fa2
Revises: 7ba4d91f4124
Create Date: 2023-09-12 19:59:55.103737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3dea3e826fa2"
down_revision = "7ba4d91f4124"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("app_config", sa.Column("monitored_library_ids_json", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("app_config", "monitored_library_ids_json")
    # ### end Alembic commands ###
