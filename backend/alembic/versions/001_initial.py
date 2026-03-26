"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create trips table
    op.create_table(
        'trips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_city', sa.String(length=255), nullable=False),
        sa.Column('to_city', sa.String(length=255), nullable=False),
        sa.Column('departure_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('available_seats', sa.Integer(), nullable=False),
        sa.Column('price_per_seat', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trips_driver_id', 'trips', ['driver_id'])
    op.create_index('ix_trips_status', 'trips', ['status'])
    
    # Create trip_requests table
    op.create_table(
        'trip_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passenger_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seats_requested', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
        sa.ForeignKeyConstraint(['passenger_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trip_requests_trip_id', 'trip_requests', ['trip_id'])
    op.create_index('ix_trip_requests_passenger_id', 'trip_requests', ['passenger_id'])
    op.create_index('ix_trip_requests_status', 'trip_requests', ['status'])
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('related_trip_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_request_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['related_trip_id'], ['trips.id'], ),
        sa.ForeignKeyConstraint(['related_request_id'], ['trip_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'])


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('notifications')
    op.drop_table('trip_requests')
    op.drop_table('trips')
    op.drop_table('users')