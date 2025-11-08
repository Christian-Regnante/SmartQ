from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Organization, Service, ServiceProvider, QueueItem, Analytics
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'admin':
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('admin.dashboard')})
            return redirect(url_for('admin.dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid admin credentials'}), 401
        flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Logout admin user"""
    logout_user()
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin.html')


# Organization Management
@admin_bp.route('/api/organizations', methods=['GET'])
@login_required
@admin_required
def get_organizations():
    """Get all organizations"""
    organizations = Organization.query.all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'type': org.type,
        'location': org.location,
        'contact_phone': org.contact_phone,
        'is_active': org.is_active,
        'services_count': org.services.count()
    } for org in organizations])


@admin_bp.route('/api/organizations', methods=['POST'])
@login_required
@admin_required
def create_organization():
    """Create new organization"""
    data = request.get_json()
    
    org = Organization(
        name=data['name'],
        type=data.get('type', ''),
        location=data.get('location', ''),
        contact_phone=data.get('contact_phone', '')
    )
    
    db.session.add(org)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': org.id,
        'message': 'Organization created successfully'
    })


@admin_bp.route('/api/organizations/<int:org_id>', methods=['PUT'])
@login_required
@admin_required
def update_organization(org_id):
    """Update organization"""
    org = Organization.query.get_or_404(org_id)
    data = request.get_json()
    
    org.name = data.get('name', org.name)
    org.type = data.get('type', org.type)
    org.location = data.get('location', org.location)
    org.contact_phone = data.get('contact_phone', org.contact_phone)
    org.is_active = data.get('is_active', org.is_active)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Organization updated'})


@admin_bp.route('/api/organizations/<int:org_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_organization(org_id):
    """Delete organization"""
    org = Organization.query.get_or_404(org_id)
    db.session.delete(org)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Organization deleted'})


# Service Management
@admin_bp.route('/api/services', methods=['GET'])
@login_required
@admin_required
def get_services():
    """Get all services"""
    services = Service.query.all()
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'organization_name': service.organization.name,
        'organization_id': service.organization_id,
        'counter_number': service.counter_number,
        'estimated_service_time': service.estimated_service_time,
        'is_active': service.is_active,
        'current_queue_length': service.get_current_queue_length()
    } for service in services])


@admin_bp.route('/api/services', methods=['POST'])
@login_required
@admin_required
def create_service():
    """Create new service"""
    data = request.get_json()
    
    service = Service(
        name=data['name'],
        organization_id=data['organization_id'],
        counter_number=data.get('counter_number', ''),
        estimated_service_time=data.get('estimated_service_time', 15)
    )
    
    db.session.add(service)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': service.id,
        'message': 'Service created successfully'
    })


@admin_bp.route('/api/services/<int:service_id>', methods=['PUT'])
@login_required
@admin_required
def update_service(service_id):
    """Update service"""
    service = Service.query.get_or_404(service_id)
    data = request.get_json()
    
    service.name = data.get('name', service.name)
    service.counter_number = data.get('counter_number', service.counter_number)
    service.estimated_service_time = data.get('estimated_service_time', service.estimated_service_time)
    service.is_active = data.get('is_active', service.is_active)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Service updated'})


@admin_bp.route('/api/services/<int:service_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_service(service_id):
    """Delete service"""
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Service deleted'})


# Service Provider Management
@admin_bp.route('/api/providers', methods=['GET'])
@login_required
@admin_required
def get_providers():
    """Get all service providers"""
    providers = ServiceProvider.query.all()
    return jsonify([{
        'id': provider.id,
        'full_name': provider.full_name,
        'username': provider.user.username,
        'email': provider.user.email,
        'phone': provider.phone,
        'service_name': provider.service.name,
        'service_id': provider.service_id,
        'is_active': provider.is_active
    } for provider in providers])


@admin_bp.route('/api/providers', methods=['POST'])
@login_required
@admin_required
def create_provider():
    """Create new service provider"""
    data = request.get_json()
    
    # Create user account
    user = User(
        username=data['username'],
        email=data['email'],
        role='staff'
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()
    
    # Create provider profile
    provider = ServiceProvider(
        user_id=user.id,
        service_id=data['service_id'],
        full_name=data['full_name'],
        phone=data.get('phone', '')
    )
    
    db.session.add(provider)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': provider.id,
        'message': 'Service provider created successfully'
    })


@admin_bp.route('/api/providers/<int:provider_id>', methods=['PUT'])
@login_required
@admin_required
def update_provider(provider_id):
    """Update service provider"""
    provider = ServiceProvider.query.get_or_404(provider_id)
    data = request.get_json()
    
    provider.full_name = data.get('full_name', provider.full_name)
    provider.phone = data.get('phone', provider.phone)
    provider.service_id = data.get('service_id', provider.service_id)
    provider.is_active = data.get('is_active', provider.is_active)
    
    if 'password' in data and data['password']:
        provider.user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Provider updated'})


@admin_bp.route('/api/providers/<int:provider_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_provider(provider_id):
    """Delete service provider"""
    provider = ServiceProvider.query.get_or_404(provider_id)
    user = provider.user
    
    db.session.delete(provider)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Provider deleted'})


# Analytics and Reports
@admin_bp.route('/api/analytics/overview', methods=['GET'])
@login_required
@admin_required
def analytics_overview():
    """Get system overview analytics"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    # Today's stats
    total_tickets_today = QueueItem.query.filter(
        QueueItem.created_at >= today_start
    ).count()
    
    completed_today = QueueItem.query.filter(
        QueueItem.created_at >= today_start,
        QueueItem.status == 'completed'
    ).count()
    
    active_now = QueueItem.query.filter_by(status='waiting').count()
    
    # Average wait time calculation
    completed_items = QueueItem.query.filter(
        QueueItem.created_at >= today_start,
        QueueItem.status == 'completed',
        QueueItem.serving_started_at.isnot(None)
    ).all()
    
    avg_wait = 0
    if completed_items:
        total_wait = sum([
            (item.serving_started_at - item.created_at).total_seconds() / 60
            for item in completed_items
        ])
        avg_wait = round(total_wait / len(completed_items), 1)
    
    return jsonify({
        'total_tickets_today': total_tickets_today,
        'completed_today': completed_today,
        'active_now': active_now,
        'average_wait_time': avg_wait,
        'total_organizations': Organization.query.count(),
        'total_services': Service.query.filter_by(is_active=True).count()
    })


@admin_bp.route('/api/analytics/services', methods=['GET'])
@login_required
@admin_required
def analytics_services():
    """Get per-service analytics"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    services = Service.query.filter_by(is_active=True).all()
    data = []
    
    for service in services:
        total = QueueItem.query.filter(
            QueueItem.service_id == service.id,
            QueueItem.created_at >= today_start
        ).count()
        
        completed = QueueItem.query.filter(
            QueueItem.service_id == service.id,
            QueueItem.created_at >= today_start,
            QueueItem.status == 'completed'
        ).count()
        
        waiting = QueueItem.query.filter(
            QueueItem.service_id == service.id,
            QueueItem.status == 'waiting'
        ).count()
        
        data.append({
            'service_name': service.name,
            'organization': service.organization.name,
            'total_today': total,
            'completed': completed,
            'waiting_now': waiting
        })
    
    return jsonify(data)