let selectedOrg = null;
let selectedService = null;
let services = [];

// Load organizations on page load
document.addEventListener('DOMContentLoaded', loadOrganizations);

async function loadOrganizations() {
    /**
     * Fetch available organizations from server and populate the org <select>.
     * Side effects: updates DOM (options in #organizationSelect) and binds change handler.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/client/api/organizations');
        const orgs = await response.json();

        const select = document.getElementById('organizationSelect');
        orgs.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.name;
            select.appendChild(option);
        });

        select.addEventListener('change', (e) => {
            if (e.target.value) {
                selectedOrg = parseInt(e.target.value);
                document.getElementById('org-selection').style.display = 'none';
                loadServices();
            }
        });
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

async function loadServices() {
    /**
     * Load services for the currently selected organization and render service buttons.
     * Uses `selectedOrg` variable. Side effects: updates `services` array and DOM.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch(`/client/api/services?org_id=${selectedOrg}`);
        services = await response.json();

        const container = document.getElementById('serviceButtons');
        container.innerHTML = services.map(service =>
            `<div class="service-btn" onclick="selectService(${service.id})">${service.name}</div>`
        ).join('');

        document.getElementById('service-selection').style.display = 'block';
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function selectService(serviceId) {
    /**
     * Select a service by id, hide services list and show phone input UI.
     * @param {number} serviceId - id of the service selected by the user
     */
    selectedService = serviceId;
    document.getElementById('service-selection').style.display = 'none';
    document.getElementById('phone-input').style.display = 'block';
}

function goBack() {
    /**
     * Cancel phone input and return to the service selection UI.
     */
    selectedService = null;
    document.getElementById('phone-input').style.display = 'none';
    document.getElementById('service-selection').style.display = 'block';
}


function goBackorg() {
    /**
     * Reset organization and service selection and show the organization picker again.
     */
    selectedOrg = null;
    selectedService = null;
    document.getElementById('organizationSelect').value = '';
    document.getElementById('service-selection').style.display = 'none';
    document.getElementById('org-selection').style.display = 'block';
}

async function joinQueue() {
    /**
     * Submit a request to join the queue for the selected service using the phone number.
     * Validates phone length, POSTs JSON to server and on success updates ticket UI.
     * @returns {Promise<void>}
     */
    const phone = document.getElementById('phoneNumber').value;

    if (!phone || phone.length < 10) {
        document.getElementById("validNumber").style.display = 'block';
        // alert('Please enter a valid phone number');
        return;
    }

    try {
        const response = await fetch('/client/api/join-queue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                service_id: selectedService,
                phone_number: phone
            })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('queueNumber').textContent = data.queue_number;
            document.getElementById('counter').textContent = data.counter;
            document.getElementById('position').textContent = data.position;
            document.getElementById('waitTime').textContent = data.estimated_wait;

            document.getElementById('phone-input').style.display = 'none';
            document.getElementById('ticket-display').style.display = 'block';
        } else {
            alert(data.error || 'Failed to join queue');
        }
    } catch (error) {
        console.error('Error joining queue:', error);
        alert('Failed to join queue');
    }
}

function reset() {
    /**
     * Reset UI to initial state for a new client session.
     * Clears selections and hides the ticket display.
     */
    selectedOrg = null;
    selectedService = null;
    document.getElementById('organizationSelect').value = '';
    document.getElementById('phoneNumber').value = '';
    document.getElementById('ticket-display').style.display = 'none';
    document.getElementById('org-selection').style.display = 'block';
    document.getElementById('service-selection').style.display = 'none';
}