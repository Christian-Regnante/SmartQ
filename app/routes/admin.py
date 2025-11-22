from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import db, User, Service, QueueItem, Organization
from datetime import datetime, date, timedelta
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, role='admin').first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['organization_id'] = user.organization_id
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin_dashboard.html')

@bp.route('/api/organization', methods=['GET'])
@admin_required
def get_organization():
    """Get admin's organization info"""
    org_id = session.get('organization_id')
    org = Organization.query.get(org_id)
    return jsonify(org.to_dict() if org else {})

@bp.route('/api/services', methods=['GET'])
@admin_required
def get_services():
    """Get all services for admin's organization"""
    org_id = session.get('organization_id')
    services = Service.query.filter_by(organization_id=org_id).all()
    return jsonify([s.to_dict() for s in services])

@bp.route('/api/services', methods=['POST'])
@admin_required
def create_service():
    """Create new service"""
    data = request.json
    org_id = session.get('organization_id')
    
    service = Service(
        name=data['name'],
        organization_id=org_id,
        counter_number=data.get('counter_number', ''),
        avg_service_time=data.get('avg_service_time', 10)
    )
    db.session.add(service)
    db.session.commit()
    return jsonify(service.to_dict())

@bp.route('/api/services/<int:service_id>', methods=['PUT'])
@admin_required
def update_service(service_id):
    """Update service"""
    org_id = session.get('organization_id')
    service = Service.query.filter_by(id=service_id, organization_id=org_id).first()
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    data = request.json
    service.name = data.get('name', service.name)
    service.counter_number = data.get('counter_number', service.counter_number)
    service.avg_service_time = data.get('avg_service_time', service.avg_service_time)
    service.is_active = data.get('is_active', service.is_active)
    
    db.session.commit()
    return jsonify(service.to_dict())

@bp.route('/api/services/<int:service_id>', methods=['DELETE'])
@admin_required
def delete_service(service_id):
    """Delete service"""
    org_id = session.get('organization_id')
    service = Service.query.filter_by(id=service_id, organization_id=org_id).first()
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    db.session.delete(service)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/api/staff', methods=['GET'])
@admin_required
def get_staff():
    """Get all staff for admin's organization"""
    org_id = session.get('organization_id')
    staff = User.query.filter_by(organization_id=org_id, role='staff').all()
    return jsonify([s.to_dict() for s in staff])

@bp.route('/api/staff', methods=['POST'])
@admin_required
def create_staff():
    """Create new staff member"""
    data = request.json
    org_id = session.get('organization_id')
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    staff = User(
        username=data['username'],
        role='staff',
        organization_id=org_id,
        service_id=data.get('service_id')
    )
    staff.set_password(data['password'])
    
    db.session.add(staff)
    db.session.commit()
    return jsonify(staff.to_dict())

@bp.route('/api/staff/<int:staff_id>', methods=['PUT'])
@admin_required
def update_staff(staff_id):
    """Update staff member"""
    org_id = session.get('organization_id')
    staff = User.query.filter_by(id=staff_id, organization_id=org_id, role='staff').first()
    
    if not staff:
        return jsonify({'error': 'Staff not found'}), 404
    
    data = request.json
    staff.service_id = data.get('service_id', staff.service_id)
    
    if data.get('password'):
        staff.set_password(data['password'])
    
    db.session.commit()
    return jsonify(staff.to_dict())

@bp.route('/api/staff/<int:staff_id>', methods=['DELETE'])
@admin_required
def delete_staff(staff_id):
    """Delete staff member"""
    org_id = session.get('organization_id')
    staff = User.query.filter_by(id=staff_id, organization_id=org_id, role='staff').first()
    
    if not staff:
        return jsonify({'error': 'Staff not found'}), 404
    
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/api/analytics', methods=['GET'])
@admin_required
def analytics():
    """Get analytics for admin's organization"""
    org_id = session.get('organization_id')
    days = request.args.get('days', 7, type=int)
    
    start_date = date.today() - timedelta(days=days)
    
    # Get all services
    services = Service.query.filter_by(organization_id=org_id).all()
    
    result = []
    for service in services:
        # Total served
        served = QueueItem.query.filter_by(service_id=service.id, status='done').filter(
            QueueItem.created_at >= start_date
        ).count()
        
        # Average wait time
        completed = QueueItem.query.filter_by(service_id=service.id, status='done').filter(
            QueueItem.created_at >= start_date,
            QueueItem.called_at.isnot(None)
        ).all()
        
        avg_wait = 0
        if completed:
            total_wait = sum([(item.called_at - item.created_at).total_seconds() / 60 
                              for item in completed])
            avg_wait = round(total_wait / len(completed), 1)
        
        result.append({
            'service_name': service.name,
            'total_served': served,
            'avg_wait_time': avg_wait
        })
    
    return jsonify(result)