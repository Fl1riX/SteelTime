"""Initial migration - fixed PostgreSQL syntax

Revision ID: 001
Revises: 
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=True),
        sa.Column('telegram_linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=False),
        sa.Column('email', sa.String(length=50), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(),  
                 nullable=False),
        sa.Column('is_entrepreneur', sa.Boolean(), 
                 server_default=sa.false(), 
                 nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('telegram_id'),
        sa.Index('ix_users_username', 'username'),
        sa.Index('ix_users_phone', 'phone'),
        sa.Index('ix_users_email', 'email'),
        sa.Index('ix_users_telegram_id', 'telegram_id')
    )
    
    # 2. services
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('duration', sa.String(length=10), nullable=False),
        sa.Column('address', sa.String(length=100), nullable=True),
        sa.Column('entrepreneur_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['entrepreneur_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'address', 'entrepreneur_id', 
                           name='uq_name_address_entrepreneur_id'),
        sa.Index('ix_services_name', 'name')
    )
    
    # 3. appointments  
    op.create_table('appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('comment', sa.String(length=1200), nullable=True),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('entrepreneur_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['entrepreneur_id'], ['users.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_id', 'entrepreneur_id', 'user_id', 'date',
                           name='uq_appointment_service_entrepreneur_user_date')
    )
    
    # 4. magic_tokens
    op.create_table('magic_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

def downgrade() -> None:
    op.drop_table('magic_tokens')
    op.drop_table('appointments')
    op.drop_table('services')
    op.drop_table('users')
