from flask import Blueprint, render_template, request, jsonify
from app.models import db, Organization, Service, QueueItem
from datetime import datetime
import random
import string

client_bp = Blueprint('client', __name__)


def generate_queue_number():
    """Generate unique queue number"""
    timestamp = datetime.utcnow().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"Q{timestamp}{random_part}"


def send_sms_notification(phone, message):
    """Mock SMS sending function - placeholder for Twilio integration"""
    print(f"📱 SMS to {phone}: {message}")
    # TODO: Implement actual Twilio integration
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(to=phone, from_=twilio_number, body=message)
    return True


@client_bp.route('/')
def index():
    """Client kiosk interface"""
    return render_template('client.html')


@client_bp.route('/api/organizations', methods=['GET'])
def get_organizations():
    """Get list of active organizations"""
    organizations = Organization.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'type': org.type,
        'location': org.location
    } for org in organizations])


@client_bp.route('/api/services/<int:org_id>', methods=['GET'])
def get_services(org_id):
    """Get services for an organization"""
    services = Service.query.filter_by(
        organization_id=org_id,
        is_active=True
    ).all()
    
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'counter': service.counter_number,
        'queue_length': service.get_current_queue_length(),
        'estimated_wait': service.get_estimated_wait_time()
    } for service in services])


@client_bp.route('/api/join-queue', methods=['POST'])
def join_queue():
    """Add client to queue"""
    data = request.get_json()
    
    service_id = data.get('service_id')
    phone = data.get('phone')
    
    if not service_id or not phone:
        return jsonify({'error': 'Service ID and phone number are required'}), 400
    
    # Validate phone number (basic Rwanda format)
    if not phone.startswith('+250') or len(phone) != 13:
        return jsonify({'error': 'Invalid phone number. Use format: +250XXXXXXXXX'}), 400
    
    # Get service
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    # Generate queue number
    queue_number = generate_queue_number()
    while QueueItem.query.filter_by(queue_number=queue_number).first():
        queue_number = generate_queue_number()
    
    # Calculate estimated wait time
    estimated_wait = service.get_estimated_wait_time()
    
    # Create queue item
    queue_item = QueueItem(
        queue_number=queue_number,
        service_id=service_id,
        client_phone=phone,
        status='waiting',
        estimated_wait_time=estimated_wait
    )
    
    db.session.add(queue_item)
    db.session.commit()
    
    # Get position in queue
    position = queue_item.get_position_in_queue()
    
    # Send SMS notification
    sms_message = f"SmartQ: Your ticket {queue_number} for {service.name} at {service.counter_number}. Position: #{position}. Estimated wait: {estimated_wait} min."
    send_sms_notification(phone, sms_message)
    
    return jsonify({
        'success': True,
        'queue_number': queue_number,
        'position': position,
        'estimated_wait': estimated_wait,
        'service_name': service.name,
        'counter': service.counter_number
    })


@client_bp.route('/api/queue-status/<queue_number>', methods=['GET'])
def queue_status(queue_number):
    """Get status of a queue ticket"""
    queue_item = QueueItem.query.filter_by(queue_number=queue_number).first()
    
    if not queue_item:
        return jsonify({'error': 'Queue ticket not found'}), 404
    
    position = queue_item.get_position_in_queue()
    
    return jsonify({
        'queue_number': queue_item.queue_number,
        'status': queue_item.status,
        'position': position,
        'service_name': queue_item.service.name,
        'counter': queue_item.service.counter_number,
        'created_at': queue_item.created_at.isoformat()
    })


@client_bp.route('/api/now-serving/<int:service_id>', methods=['GET'])
def now_serving(service_id):
    """Get currently serving ticket for a service"""
    serving = QueueItem.query.filter_by(
        service_id=service_id,
        status='serving'
    ).order_by(QueueItem.serving_started_at.desc()).first()
    
    waiting_count = QueueItem.query.filter_by(
        service_id=service_id,
        status='waiting'
    ).count()
    
    service = Service.query.get(service_id)
    
    return jsonify({
        'service_name': service.name if service else '',
        'counter': service.counter_number if service else '',
        'now_serving': serving.queue_number if serving else None,
        'waiting_count': waiting_count
    })


@client_bp.route('/display')
def display_screen():
    """Now serving display screen"""
    return render_template('display.html')