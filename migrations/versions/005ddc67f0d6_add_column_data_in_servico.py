"""Add column data in Servico

Revision ID: 005ddc67f0d6
Revises: d3cd6f4d3fcd
Create Date: 2020-11-24 09:35:39.616707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005ddc67f0d6'
down_revision = 'd3cd6f4d3fcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('servico', sa.Column('data', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('servico', 'data')
    # ### end Alembic commands ###
