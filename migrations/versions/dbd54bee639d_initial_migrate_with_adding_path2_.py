"""initial migrate with adding path2 column to gallery table

Revision ID: dbd54bee639d
Revises: 
Create Date: 2024-03-03 22:33:47.346485

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'dbd54bee639d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery', schema=None) as batch_op:
        batch_op.add_column(sa.Column('path1', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('path2', sa.String(length=100), nullable=True))
        batch_op.drop_column('path')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery', schema=None) as batch_op:
        batch_op.add_column(sa.Column('path', mysql.VARCHAR(length=100), nullable=True))
        batch_op.drop_column('path2')
        batch_op.drop_column('path1')

    # ### end Alembic commands ###