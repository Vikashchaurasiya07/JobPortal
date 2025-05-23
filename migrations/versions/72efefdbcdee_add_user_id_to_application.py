"""Add user_id to Application

Revision ID: 72efefdbcdee
Revises: 6f8ac59dbc17
Create Date: 2025-05-09 00:26:56.667434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72efefdbcdee'
down_revision = '6f8ac59dbc17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('application')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('application',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('job_id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('cover_letter', sa.TEXT(), nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), nullable=True),
    sa.Column('applied_on', sa.DATETIME(), nullable=True),
    sa.Column('resume_link', sa.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
