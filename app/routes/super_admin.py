from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import db, User, Organization, Service
from functools import wraps

bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'super_admin':
            return redirect(url_for('super_admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('super_admin_login.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, role='super_admin').first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('super_admin.login'))

@bp.route('/dashboard')
@super_admin_required
def dashboard():
    return render_template('super_admin_dashboard.html')

# Organization Management
@bp.route('/api/organizations', methods=['GET'])
@super_admin_required
def get_organizations():
    """Get all organizations with stats"""
    orgs = Organization.query.all()
    result = []
    
    for org in orgs:
        admin_count = User.query.filter_by(organization_id=org.id, role='admin').count()
        service_count = Service.query.filter_by(organization_id=org.id).count()
        staff_count = User.query.filter_by(organization_id=org.id, role='staff').count()
        
        result.append({
            **org.to_dict(),
            'admin_count': admin_count,
            'service_count': service_count,
            'staff_count': staff_count
        })
    
    return jsonify(result)

@bp.route('/api/organizations', methods=['POST'])
@super_admin_required
def create_organization():
    """Create new organization"""
    data = request.json
    
    org = Organization(
        name=data['name'],
        location=data.get('location', ''),
        contact=data.get('contact', '')
    )
    db.session.add(org)
    db.session.commit()
    return jsonify(org.to_dict())

@bp.route('/api/organizations/<int:org_id>', methods=['PUT'])
@super_admin_required
def update_organization(org_id):
    """Update organization"""
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.json
    org.name = data.get('name', org.name)
    org.location = data.get('location', org.location)
    org.contact = data.get('contact', org.contact)
    
    db.session.commit()
    return jsonify(org.to_dict())

@bp.route('/api/organizations/<int:org_id>', methods=['DELETE'])
@super_admin_required
def delete_organization(org_id):
    """Delete organization"""
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    db.session.delete(org)
    db.session.commit()
    return jsonify({'success': True})

# Admin Management
@bp.route('/api/admins', methods=['GET'])
@super_admin_required
def get_admins():
    """Get all organization admins"""
    admins = User.query.filter_by(role='admin').all()
    result = []
    
    for admin in admins:
        org = Organization.query.get(admin.organization_id) if admin.organization_id else None
        result.append({
            **admin.to_dict(),
            'organization_name': org.name if org else 'None'
        })
    
    return jsonify(result)

@bp.route('/api/admins', methods=['POST'])
@super_admin_required
def create_admin():
    """Create new organization admin"""
    data = request.json
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    admin = User(
        username=data['username'],
        role='admin',
        organization_id=data.get('organization_id')
    )
    admin.set_password(data['password'])
    
    db.session.add(admin)
    db.session.commit()
    return jsonify(admin.to_dict())

@bp.route('/api/admins/<int:admin_id>', methods=['PUT'])
@super_admin_required
def update_admin(admin_id):
    """Update admin"""
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    data = request.json
    admin.organization_id = data.get('organization_id', admin.organization_id)
    
    if data.get('password'):
        admin.set_password(data['password'])
    
    db.session.commit()
    return jsonify(admin.to_dict())

@bp.route('/api/admins/<int:admin_id>', methods=['DELETE'])
@super_admin_required
def delete_admin(admin_id):
    """Delete admin"""
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    db.session.delete(admin)
    db.session.commit()
    return jsonify({'success': True})

# Overview Stats
@bp.route('/api/overview', methods=['GET'])
@super_admin_required
def overview():
    """Get system overview statistics"""
    total_orgs = Organization.query.count()
    total_admins = User.query.filter_by(role='admin').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_services = Service.query.count()
    
    return jsonify({
        'total_organizations': total_orgs,
        'total_admins': total_admins,
        'total_staff': total_staff,
        'total_services': total_services
    })