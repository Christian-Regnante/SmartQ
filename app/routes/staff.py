from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, ServiceProvider, QueueItem, Service
from datetime import datetime

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Staff login page"""
    if current_user.is_authenticated:
        return redirect(url_for('staff.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'staff':
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('staff.dashboard')})
            return redirect(url_for('staff.dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid username or password', 'error')
    
    return render_template('staff_login.html')


@staff_bp.route('/logout')
@login_required
def logout():
    """Logout staff user"""
    logout_user()
    return redirect(url_for('staff.login'))


@staff_bp.route('/dashboard')
@login_required
def dashboard():
    """Staff dashboard"""
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('staff.login'))
    
    return render_template('dashboard.html')


@staff_bp.route('/api/my-service', methods=['GET'])
@login_required
def get_my_service():
    """Get service provider's assigned service"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    service = provider.service
    
    return jsonify({
        'service_id': service.id,
        'service_name': service.name,
        'counter': service.counter_number,
        'provider_name': provider.full_name
    })


@staff_bp.route('/api/queue', methods=['GET'])
@login_required
def get_queue():
    """Get queue for staff member's service"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    # Get waiting queue items
    waiting = QueueItem.query.filter_by(
        service_id=provider.service_id,
        status='waiting'
    ).order_by(QueueItem.priority.desc(), QueueItem.created_at).all()
    
    # Get currently serving
    serving = QueueItem.query.filter_by(
        service_id=provider.service_id,
        status='serving'
    ).first()
    
    return jsonify({
        'waiting': [{
            'id': item.id,
            'queue_number': item.queue_number,
            'phone': item.client_phone[-4:],  # Last 4 digits for privacy
            'created_at': item.created_at.strftime('%H:%M'),
            'position': item.get_position_in_queue()
        } for item in waiting],
        'serving': {
            'id': serving.id,
            'queue_number': serving.queue_number,
            'phone': serving.client_phone[-4:],
            'serving_since': serving.serving_started_at.strftime('%H:%M')
        } if serving else None
    })


@staff_bp.route('/api/call-next', methods=['POST'])
@login_required
def call_next():
    """Call next client in queue"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    # Check if already serving someone
    serving = QueueItem.query.filter_by(
        service_id=provider.service_id,
        status='serving'
    ).first()
    
    if serving:
        return jsonify({'error': 'Already serving a client. Complete current service first.'}), 400
    
    # Get next in queue
    next_item = QueueItem.query.filter_by(
        service_id=provider.service_id,
        status='waiting'
    ).order_by(QueueItem.priority.desc(), QueueItem.created_at).first()
    
    if not next_item:
        return jsonify({'error': 'No clients in queue'}), 404
    
    # Mark as serving
    next_item.mark_serving()
    
    return jsonify({
        'success': True,
        'queue_number': next_item.queue_number,
        'phone': next_item.client_phone[-4:]
    })


@staff_bp.route('/api/complete/<int:item_id>', methods=['POST'])
@login_required
def complete_service(item_id):
    """Mark service as completed"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    item = QueueItem.query.get(item_id)
    
    if not item or item.service_id != provider.service_id:
        return jsonify({'error': 'Queue item not found'}), 404
    
    if item.status != 'serving':
        return jsonify({'error': 'Item is not being served'}), 400
    
    item.mark_completed()
    
    return jsonify({'success': True})


@staff_bp.route('/api/skip/<int:item_id>', methods=['POST'])
@login_required
def skip_client(item_id):
    """Skip a client (no-show)"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    item = QueueItem.query.get(item_id)
    
    if not item or item.service_id != provider.service_id:
        return jsonify({'error': 'Queue item not found'}), 404
    
    item.mark_skipped()
    
    return jsonify({'success': True})


@staff_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get statistics for staff dashboard"""
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    
    if not provider:
        return jsonify({'error': 'Service provider profile not found'}), 404
    
    served_today = provider.get_served_today()
    avg_service_time = provider.get_average_service_time()
    
    waiting_count = QueueItem.query.filter_by(
        service_id=provider.service_id,
        status='waiting'
    ).count()
    
    return jsonify({
        'served_today': served_today,
        'average_service_time': avg_service_time,
        'waiting_count': waiting_count
    })