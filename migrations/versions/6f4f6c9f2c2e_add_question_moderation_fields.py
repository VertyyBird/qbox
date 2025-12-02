# Qbox, a Q&A website
# Copyright (C) 2025  Rhys Baker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Add moderation fields to Question

Revision ID: 6f4f6c9f2c2e
Revises: 5c92b7e0c9e3
Create Date: 2025-02-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f4f6c9f2c2e'
down_revision = '5c92b7e0c9e3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table('question') as batch_op:
        batch_op.alter_column('is_hidden', server_default=None)
        batch_op.alter_column('is_flagged', server_default=None)


def downgrade():
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_column('is_flagged')
        batch_op.drop_column('is_hidden')
