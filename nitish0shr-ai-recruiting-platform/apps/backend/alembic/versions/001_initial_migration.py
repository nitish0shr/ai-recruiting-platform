"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), unique=True, nullable=True),
        sa.Column('settings', sa.JSON, default=dict),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', sa.Enum('admin', 'recruiter', 'hiring_manager', 'interviewer', name='userrole'), nullable=False, default='recruiter'),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('requirements', sa.JSON, default=list),
        sa.Column('parsed_requirements', sa.JSON, default=dict),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('salary_min', sa.Float, nullable=True),
        sa.Column('salary_max', sa.Float, nullable=True),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create candidates table
    op.create_table(
        'candidates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('linkedin_url', sa.String(255), nullable=True),
        sa.Column('resume_text', sa.Text, nullable=True),
        sa.Column('resume_parsed', sa.JSON, default=dict),
        sa.Column('skills', sa.JSON, default=list),
        sa.Column('experience_years', sa.Float, nullable=True),
        sa.Column('current_company', sa.String(255), nullable=True),
        sa.Column('current_title', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('status', sa.Enum('new', 'screening', 'interview', 'offer', 'hired', 'rejected', name='applicationstatus'), default='new'),
        sa.Column('fit_score', sa.Float, nullable=True),
        sa.Column('fit_score_details', sa.JSON, default=dict),
        sa.Column('source', sa.String(50), default='direct'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('applied_at', sa.DateTime, default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('application_id', UUID(as_uuid=True), sa.ForeignKey('applications.id'), nullable=False),
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('interviewer_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime, nullable=False),
        sa.Column('duration_minutes', sa.Integer, default=60),
        sa.Column('type', sa.String(50), default='video'),
        sa.Column('status', sa.Enum('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', name='interviewstatus'), default='scheduled'),
        sa.Column('meeting_link', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('feedback', sa.JSON, default=dict),
        sa.Column('rating', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('template_id', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', name='campaignstatus'), default='draft'),
        sa.Column('target_criteria', sa.JSON, default=dict),
        sa.Column('sent_count', sa.Integer, default=0),
        sa.Column('opened_count', sa.Integer, default=0),
        sa.Column('clicked_count', sa.Integer, default=0),
        sa.Column('replied_count', sa.Integer, default=0),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create emails table
    op.create_table(
        'emails',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('candidate_id', UUID(as_uuid=True), sa.ForeignKey('candidates.id'), nullable=False),
        sa.Column('recipient_email', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), default='sent'),
        sa.Column('sent_at', sa.DateTime, nullable=True),
        sa.Column('opened_at', sa.DateTime, nullable=True),
        sa.Column('clicked_at', sa.DateTime, nullable=True),
        sa.Column('replied_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('application_id', UUID(as_uuid=True), sa.ForeignKey('applications.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('questions', sa.JSON, default=list),
        sa.Column('responses', sa.JSON, default=dict),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # Create analytics table
    op.create_table(
        'analytics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('dimensions', sa.JSON, default=dict),
        sa.Column('date', sa.DateTime, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('data', sa.JSON, default=dict),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # Create indexes
    op.create_index('idx_job_candidate', 'applications', ['job_id', 'candidate_id'], unique=True)
    op.create_index('idx_status', 'applications', ['status'])
    op.create_index('idx_fit_score', 'applications', ['fit_score'])
    op.create_index('idx_org_metric_date', 'analytics', ['organization_id', 'metric_type', 'date'])
    op.create_index('idx_user_unread', 'notifications', ['user_id', 'is_read'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('notifications')
    op.drop_table('analytics')
    op.drop_table('assessments')
    op.drop_table('emails')
    op.drop_table('campaigns')
    op.drop_table('interviews')
    op.drop_table('applications')
    op.drop_table('candidates')
    op.drop_table('jobs')
    op.drop_table('users')
    op.drop_table('organizations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS applicationstatus')
    op.execute('DROP TYPE IF EXISTS interviewstatus')
    op.execute('DROP TYPE IF EXISTS campaignstatus')