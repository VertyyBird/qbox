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

"""Add public_id to Answer for permalinks

Revision ID: 5c92b7e0c9e3
Revises: d72127b894bb
Create Date: 2025-02-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import secrets


# revision identifiers, used by Alembic.
revision = '5c92b7e0c9e3'
down_revision = '55a7297d52af'
branch_labels = None
depends_on = None


def _generate_unique_public_id(existing_ids):
    while True:
        candidate = secrets.token_hex(8)
        if candidate not in existing_ids:
            return candidate


def upgrade():
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('public_id', sa.String(length=16), nullable=True))

    bind = op.get_bind()
    answers_table = sa.table(
        'answer',
        sa.column('id', sa.Integer),
        sa.column('public_id', sa.String(length=16)),
    )

    existing_ids = set()
    result = bind.execute(sa.select(answers_table.c.id, answers_table.c.public_id))
    for row in result:
        public_id = _generate_unique_public_id(existing_ids)
        existing_ids.add(public_id)
        bind.execute(
            answers_table.update()
            .where(answers_table.c.id == row.id)
            .values(public_id=public_id)
        )

    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('public_id', existing_type=sa.String(length=16), nullable=False)
        batch_op.create_index(batch_op.f('ix_answer_public_id'), ['public_id'], unique=True)


def downgrade():
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_answer_public_id'))
        batch_op.drop_column('public_id')
