from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import db, User, QueueItem, Service
from datetime import datetime, date
from functools import wraps

bp = Blueprint('staff', __name__, url_prefix='/staff')

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'staff':
            return redirect(url_for('staff.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('staff_login.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, role='staff').first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['service_id'] = user.service_id
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('staff.login'))

@bp.route('/dashboard')
@staff_required
def dashboard():
    return render_template('staff_dashboard.html')

@bp.route('/api/queue', methods=['GET'])
@staff_required
def get_queue():
    """Get queue for staff's assigned service"""
    service_id = session.get('service_id')
    if not service_id:
        return jsonify({'error': 'No service assigned'}), 400
    
    # Get all queue items for today
    today = date.today()
    queue_items = QueueItem.query.filter_by(service_id=service_id).filter(
        db.func.date(QueueItem.created_at) == today
    ).order_by(QueueItem.created_at).all()
    
    return jsonify([item.to_dict() for item in queue_items])

@bp.route('/api/service-info', methods=['GET'])
@staff_required
def service_info():
    """Get service information"""
    service_id = session.get('service_id')
    if not service_id:
        return jsonify({'error': 'No service assigned'}), 400
    
    service = Service.query.get(service_id)
    return jsonify(service.to_dict())

@bp.route('/api/call-next', methods=['POST'])
@staff_required
def call_next():
    """Call next person in queue"""
    service_id = session.get('service_id')
    
    # Mark any currently serving as done
    current = QueueItem.query.filter_by(service_id=service_id, status='serving').first()
    if current:
        current.status = 'done'
        current.completed_at = datetime.now()
    
    # Get next waiting
    next_item = QueueItem.query.filter_by(
        service_id=service_id,
        status='waiting'
    ).order_by(QueueItem.created_at).first()
    
    if next_item:
        next_item.status = 'serving'
        next_item.called_at = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'queue_item': next_item.to_dict()})
    
    db.session.commit()
    return jsonify({'success': False, 'message': 'No one waiting'})

@bp.route('/api/mark-done/<int:item_id>', methods=['POST'])
@staff_required
def mark_done(item_id):
    """Mark current client as done"""
    item = QueueItem.query.get(item_id)
    if item and item.service_id == session.get('service_id'):
        item.status = 'done'
        item.completed_at = datetime.now()
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Item not found'}), 404

@bp.route('/api/skip/<int:item_id>', methods=['POST'])
@staff_required
def skip(item_id):
    """Skip a client"""
    item = QueueItem.query.get(item_id)
    if item and item.service_id == session.get('service_id'):
        item.status = 'skipped'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Item not found'}), 404

@bp.route('/api/stats', methods=['GET'])
@staff_required
def stats():
    """Get daily stats"""
    service_id = session.get('service_id')
    today = date.today()
    
    # Total served today
    served = QueueItem.query.filter_by(service_id=service_id, status='done').filter(
        db.func.date(QueueItem.created_at) == today
    ).count()
    
    # Calculate average wait time
    completed = QueueItem.query.filter_by(service_id=service_id, status='done').filter(
        db.func.date(QueueItem.created_at) == today,
        QueueItem.called_at.isnot(None)
    ).all()
    
    avg_wait = 0
    if completed:
        total_wait = sum([(item.called_at - item.created_at).total_seconds() / 60 
                          for item in completed])
        avg_wait = round(total_wait / len(completed), 1)
    
    # Currently waiting
    waiting = QueueItem.query.filter_by(service_id=service_id, status='waiting').count()
    
    return jsonify({
        'served_today': served,
        'avg_wait_time': avg_wait,
        'currently_waiting': waiting
    })