"""Add production consumption for resources

Revision ID: f14de851eec6
Revises: 385b3823fd85
Create Date: 2025-04-22 18:16:29.750472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f14de851eec6'
down_revision: Union[str, None] = '385b3823fd85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pp_tracking', sa.Column('token_symbol', sa.String(), nullable=True))
    op.add_column('pp_tracking', sa.Column('total_supply', sa.BigInteger(), nullable=True))
    op.add_column('pp_tracking', sa.Column('rewards_per_hour', sa.BigInteger(), nullable=True))
    op.add_column('pp_tracking', sa.Column('cost_per_h_grain', sa.BigInteger(), nullable=True))
    op.add_column('pp_tracking', sa.Column('cost_per_h_wood', sa.BigInteger(), nullable=True))
    op.add_column('pp_tracking', sa.Column('cost_per_h_stone', sa.BigInteger(), nullable=True))
    op.add_column('pp_tracking', sa.Column('cost_per_h_iron', sa.BigInteger(), nullable=True))
    op.rename_table('resource_metrics', 'resource_hub_metrics')
    op.rename_table('pp_tracking', 'resource_tracking')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('resource_tracking', 'cost_per_h_iron')
    op.drop_column('resource_tracking', 'cost_per_h_stone')
    op.drop_column('resource_tracking', 'cost_per_h_wood')
    op.drop_column('resource_tracking', 'cost_per_h_grain')
    op.drop_column('resource_tracking', 'rewards_per_hour')
    op.drop_column('resource_tracking', 'total_supply')
    op.drop_column('resource_tracking', 'token_symbol')

    op.rename_table('resource_hub_metrics', 'resource_metrics')
    op.rename_table('resource_tracking', 'pp_tracking')
    # ### end Alembic commands ###
