let selectedOrgId = null;
let selectedServiceId = null;
let currentStep = 1;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadOrganizations();
});

// Load organizations
async function loadOrganizations() {
    try {
        const response = await fetch('/client/api/organizations');
        const organizations = await response.json();
        
        const container = document.getElementById('organizationsList');
        container.innerHTML = '';
        
        organizations.forEach(org => {
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => selectOrganization(org.id);
            card.innerHTML = `
                <h3>${org.name}</h3>
                <p>${org.location || ''}</p>
                <span class="badge">${org.type || 'Service'}</span>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

// Select organization and load services
async function selectOrganization(orgId) {
    selectedOrgId = orgId;
    
    try {
        const response = await fetch(`/client/api/services/${orgId}`);
        const services = await response.json();
        
        const container = document.getElementById('servicesList');
        container.innerHTML = '';
        
        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => selectService(service.id);
            card.innerHTML = `
                <h3>${service.name}</h3>
                <p><strong>Counter:</strong> ${service.counter}</p>
                <p><strong>Queue:</strong> ${service.queue_length} people</p>
                <p><strong>Wait:</strong> ~${service.estimated_wait} min</p>
            `;
            container.appendChild(card);
        });
        
        goToStep(2);
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

// Select service
function selectService(serviceId) {
    selectedServiceId = serviceId;
    goToStep(3);
}

// Join queue
async function joinQueue() {
    const phone = document.getElementById('phoneInput').value.trim();
    
    if (!phone) {
        alert('Please enter your phone number');
        return;
    }
    
    if (!phone.startsWith('+250') || phone.length !== 13) {
        alert('Please enter a valid Rwandan phone number (+250XXXXXXXXX)');
        return;
    }
    
    try {
        const response = await fetch('/client/api/join-queue', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                service_id: selectedServiceId,
                phone: phone
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display ticket
            document.getElementById('ticketNumber').textContent = data.queue_number;
            document.getElementById('serviceName').textContent = data.service_name;
            document.getElementById('counterNumber').textContent = data.counter;
            document.getElementById('queuePosition').textContent = data.position;
            document.getElementById('estimatedWait').textContent = data.estimated_wait;
            
            goToStep(4);
        } else {
            alert(data.error || 'Failed to join queue');
        }
    } catch (error) {
        console.error('Error joining queue:', error);
        alert('Network error. Please try again.');
    }
}

// Navigation
function goToStep(step) {
    document.querySelectorAll('.kiosk-step').forEach(el => el.classList.remove('active'));
    document.getElementById(`step${step}`).classList.add('active');
    currentStep = step;
}

function goBack() {
    if (currentStep > 1) {
        goToStep(currentStep - 1);
    }
}

function startOver() {
    selectedOrgId = null;
    selectedServiceId = null;
    document.getElementById('phoneInput').value = '';
    goToStep(1);
    loadOrganizations();
}