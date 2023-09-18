"""attacment

Revision ID: 563d3e4f8ef0
Revises: 9b0757283a5b
Create Date: 2023-09-09 21:49:36.943792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '563d3e4f8ef0'
down_revision = '9b0757283a5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('original_filename', sa.String(length=256), nullable=False),
    sa.Column('url', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_files_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_files')),
    sa.UniqueConstraint('url', name=op.f('uq_files_url'))
    )
    op.create_index(op.f('ix_files_uuid'), 'files', ['uuid'], unique=True)
    op.create_table('attachments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], name=op.f('fk_attachments_file_id_files')),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], name=op.f('fk_attachments_job_id_jobs')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_attachments_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_attachments'))
    )
    op.create_index(op.f('ix_attachments_uuid'), 'attachments', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_attachments_uuid'), table_name='attachments')
    op.drop_table('attachments')
    op.drop_index(op.f('ix_files_uuid'), table_name='files')
    op.drop_table('files')
    # ### end Alembic commands ###