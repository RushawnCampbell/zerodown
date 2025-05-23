"""empty message

Revision ID: d5d8ad58ca2e
Revises: 96e629487cc1
Create Date: 2025-04-17 18:57:49.115948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5d8ad58ca2e'
down_revision = '96e629487cc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('esnpair',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('storage_node_id', sa.String(length=36), nullable=False),
    sa.Column('endpoint_id', sa.String(length=36), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['endpoint_id'], ['endpoint.id'], ),
    sa.ForeignKeyConstraint(['storage_node_id'], ['storagenode.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('endpoint_id'),
    sa.UniqueConstraint('storage_node_id')
    )
    op.create_table('backupjob',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('esnpair', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('target', sa.Text(), nullable=True),
    sa.Column('destination', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('last_backup', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['esnpair'], ['esnpair.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('backupjob')
    op.drop_table('esnpair')
    # ### end Alembic commands ###
