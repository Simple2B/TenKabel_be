"""init

Revision ID: f9852f5b3f30
Revises: 
Create Date: 2023-04-26 17:20:19.850408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9852f5b3f30'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('uuid', sa.VARCHAR(length=36), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('title', sa.VARCHAR(length=64), nullable=False),
    sa.Column('content', sa.VARCHAR(length=512), nullable=False),
    sa.Column('is_published', sa.BOOLEAN(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
