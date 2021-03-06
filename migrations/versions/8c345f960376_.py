"""empty message

Revision ID: 8c345f960376
Revises: 3c403aee5d08
Create Date: 2021-12-06 08:30:36.942438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c345f960376'
down_revision = '3c403aee5d08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('site',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=80), nullable=False),
    sa.Column('country', sa.String(length=3), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('used', sa.Integer(), nullable=True),
    sa.Column('available', sa.Integer(), nullable=True),
    sa.Column('admin_area', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('site')
    # ### end Alembic commands ###
