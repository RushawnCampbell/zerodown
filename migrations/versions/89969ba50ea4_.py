"""empty message

Revision ID: 89969ba50ea4
Revises: 0b0a2dca237a
Create Date: 2025-03-10 16:18:43.865015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '89969ba50ea4'
down_revision = '0b0a2dca237a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('endpoint', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
        batch_op.alter_column('ip',
               existing_type=mysql.VARCHAR(length=15),
               nullable=False)
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('endpoint', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
        batch_op.alter_column('ip',
               existing_type=mysql.VARCHAR(length=15),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###
