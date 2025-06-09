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

"""Add bio and avatar_url to User

Revision ID: 55a7297d52af
Revises: d72127b894bb
Create Date: 2025-06-08 20:03:31
"""
from alembic import op
import sqlalchemy as sa

revision = '55a7297d52af'
down_revision = 'd72127b894bb'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('avatar_url', sa.String(length=255), nullable=True))

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('avatar_url')
        batch_op.drop_column('bio')
