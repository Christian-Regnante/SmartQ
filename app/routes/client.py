from flask import Blueprint, render_template, request, jsonify
from app.models import db, Service, QueueItem, Organization
from datetime import datetime, date
import random

bp = Blueprint('client', __name__, url_prefix='/client')

def send_sms_mock(phone, message):
    """Mock SMS sending - replace with Twilio in production"""
    print(f"📱 SMS to {phone}: {message}")
    return True

@bp.route('/')
def index():
    """Client kiosk interface"""
    return render_template('client.html')

@bp.route('/api/organizations', methods=['GET'])
def get_organizations():
    """Get all organizations for selection"""
    orgs = Organization.query.all()
    return jsonify([org.to_dict() for org in orgs])

@bp.route('/api/services', methods=['GET'])
def get_services():
    """Get all active services for an organization"""
    org_id = request.args.get('org_id', type=int)
    if not org_id:
        return jsonify({'error': 'Organization ID required'}), 400
    
    services = Service.query.filter_by(organization_id=org_id, is_active=True).all()
    return jsonify([s.to_dict() for s in services])

@bp.route('/api/join-queue', methods=['POST'])
def join_queue():
    """Add client to queue"""
    data = request.json
    service_id = data.get('service_id')
    phone = data.get('phone_number')
    
    if not service_id or not phone:
        return jsonify({'error': 'Service and phone number required'}), 400
    
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    # Generate queue number
    today = date.today()
    count = QueueItem.query.filter_by(service_id=service_id).filter(
        db.func.date(QueueItem.created_at) == today
    ).count()
    
    queue_number = f"{service.name[:3].upper()}{count + 1:03d}"
    
    # Calculate estimated wait time
    waiting = QueueItem.query.filter_by(service_id=service_id, status='waiting').count()
    estimated_wait = waiting * service.avg_service_time
    
    # Create queue item
    queue_item = QueueItem(
        queue_number=queue_number,
        service_id=service_id,
        phone_number=phone,
        status='waiting'
    )
    db.session.add(queue_item)
    db.session.commit()
    
    # Send SMS
    sms_message = f"SmartQ: Your ticket {queue_number} for {service.name}. Counter: {service.counter_number}. Est. wait: {estimated_wait} min."
    send_sms_mock(phone, sms_message)
    
    return jsonify({
        'success': True,
        'queue_number': queue_number,
        'counter': service.counter_number,
        'estimated_wait': estimated_wait,
        'position': waiting + 1
    })

@bp.route('/display')
def display():
    """Unified display screen for all services in an organization"""
    return render_template('client_display.html')

@bp.route('/api/display-status', methods=['GET'])
def display_status():
    """Get current serving status for all services in an organization"""
    org_id = request.args.get('org_id', type=int)
    if not org_id:
        return jsonify({'error': 'Organization ID required'}), 400
    
    services = Service.query.filter_by(organization_id=org_id, is_active=True).all()
    
    result = []
    for service in services:
        # Get currently serving
        serving = QueueItem.query.filter_by(
            service_id=service.id,
            status='serving'
        ).order_by(QueueItem.called_at.desc()).first()
        
        # Get next in queue
        next_item = QueueItem.query.filter_by(
            service_id=service.id,
            status='waiting'
        ).order_by(QueueItem.created_at).first()
        
        # Get waiting count
        waiting_count = QueueItem.query.filter_by(
            service_id=service.id,
            status='waiting'
        ).count()
        
        result.append({
            'service_name': service.name,
            'counter': service.counter_number,
            'now_serving': serving.queue_number if serving else None,
            'next': next_item.queue_number if next_item else None,
            'waiting': waiting_count
        })
    
    return jsonify(result)