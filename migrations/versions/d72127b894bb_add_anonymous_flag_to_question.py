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

"""Add is_anonymous flag to Question

Revision ID: d72127b894bb
Revises: aca2875d8b68
Create Date: 2025-01-15 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd72127b894bb'
down_revision = 'aca2875d8b68'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_question")
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table('question') as batch_op:
        batch_op.alter_column('is_anonymous', server_default=None)


def downgrade():
    with op.batch_alter_table('question', schema=None) as batch_op:
        batch_op.drop_column('is_anonymous')
