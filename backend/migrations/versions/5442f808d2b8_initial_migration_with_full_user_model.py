from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta
# revision identifiers
revision = '5442f808d2b8'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('password', sa.String(200), nullable=True),
        sa.Column('role', sa.String(50), nullable=False, server_default='user'),
        sa.Column('full_name', sa.String(150), nullable=False, server_default='Unknown'),
        sa.Column('initials', sa.String(10), nullable=True),
        sa.Column('contact_number', sa.String(20), nullable=True),
        sa.Column('address', sa.String(250), nullable=True),
        sa.Column('guardian_name', sa.String(150), nullable=True),
        sa.Column('guardian_number', sa.String(20), nullable=True)
    )

    # Remove server defaults after creation
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('full_name', server_default=None)
        batch_op.alter_column('role', server_default=None)

def downgrade():
    op.drop_table('user')
