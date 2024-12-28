"""empty message

Revision ID: f48cf62fbbf3
Revises: 3579fbf58f2a
Create Date: 2024-09-26 14:07:50.848818

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f48cf62fbbf3'
down_revision = '3579fbf58f2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False))
        batch_op.drop_column('unit_price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit_price', mysql.DECIMAL(precision=10, scale=2), nullable=False))
        batch_op.drop_column('price')

    # ### end Alembic commands ###
