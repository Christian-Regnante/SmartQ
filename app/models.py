from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Organization(db.Model):
    """Represents organizations like hospitals, banks, etc."""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    type = db.Column(db.String(100))  # hospital, bank, government, etc.
    location = db.Column(db.String(200))
    contact_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    services = db.relationship('Service', backref='organization', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Organization {self.name}>'


class Service(db.Model):
    """Represents services offered by organizations"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    counter_number = db.Column(db.String(50))  # Counter/Room identifier
    estimated_service_time = db.Column(db.Integer, default=15)  # minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    queue_items = db.relationship('QueueItem', backref='service', lazy='dynamic')
    service_providers = db.relationship('ServiceProvider', backref='service', lazy='dynamic')
    
    # Add index for faster queries
    __table_args__ = (
        db.Index('idx_org_active', 'organization_id', 'is_active'),
    )
    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    def get_current_queue_length(self):
        """Get count of pending queue items"""
        return self.queue_items.filter_by(status='waiting').count()
    
    def get_estimated_wait_time(self):
        """Calculate estimated wait time based on queue length"""
        queue_length = self.get_current_queue_length()
        return queue_length * self.estimated_service_time


class User(UserMixin, db.Model):
    """Base user model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, staff
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ServiceProvider(db.Model):
    """Staff members who serve clients"""
    __tablename__ = 'service_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='service_provider_profile')
    
    def __repr__(self):
        return f'<ServiceProvider {self.full_name}>'
    
    def get_served_today(self):
        """Count of clients served today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return QueueItem.query.filter(
            QueueItem.service_id == self.service_id,
            QueueItem.status == 'completed',
            QueueItem.completed_at >= today_start
        ).count()
    
    def get_average_service_time(self):
        """Calculate average service time in minutes"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed = QueueItem.query.filter(
            QueueItem.service_id == self.service_id,
            QueueItem.status == 'completed',
            QueueItem.completed_at >= today_start,
            QueueItem.serving_started_at.isnot(None)
        ).all()
        
        if not completed:
            return 0
        
        total_time = sum([
            (item.completed_at - item.serving_started_at).total_seconds() / 60
            for item in completed
        ])
        return round(total_time / len(completed), 1)


class QueueItem(db.Model):
    """Individual queue tickets"""
    __tablename__ = 'queue_items'
    
    id = db.Column(db.Integer, primary_key=True)
    queue_number = db.Column(db.String(50), unique=True, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='waiting')  # waiting, serving, completed, skipped, cancelled
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    called_at = db.Column(db.DateTime)
    serving_started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Metadata
    estimated_wait_time = db.Column(db.Integer)  # minutes
    notes = db.Column(db.Text)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_service_status', 'service_id', 'status'),
        db.Index('idx_queue_number', 'queue_number'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f'<QueueItem {self.queue_number}>'
    
    def get_position_in_queue(self):
        """Get current position in the queue"""
        if self.status != 'waiting':
            return 0
        
        return QueueItem.query.filter(
            QueueItem.service_id == self.service_id,
            QueueItem.status == 'waiting',
            db.or_(
                QueueItem.priority > self.priority,
                db.and_(
                    QueueItem.priority == self.priority,
                    QueueItem.created_at < self.created_at
                )
            )
        ).count() + 1
    
    def mark_serving(self):
        """Mark item as being served"""
        self.status = 'serving'
        self.serving_started_at = datetime.utcnow()
        db.session.commit()
    
    def mark_completed(self):
        """Mark item as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_skipped(self):
        """Mark item as skipped"""
        self.status = 'skipped'
        db.session.commit()


class Analytics(db.Model):
    """Store daily analytics for reporting"""
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    
    # Metrics
    total_tickets = db.Column(db.Integer, default=0)
    completed_tickets = db.Column(db.Integer, default=0)
    skipped_tickets = db.Column(db.Integer, default=0)
    average_wait_time = db.Column(db.Float, default=0.0)  # minutes
    average_service_time = db.Column(db.Float, default=0.0)  # minutes
    peak_queue_length = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_date_org', 'date', 'organization_id'),
    )
    
    def __repr__(self):
        return f'<Analytics {self.date}>'