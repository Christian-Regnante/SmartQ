let currentServices = [];

document.addEventListener('DOMContentLoaded', () => {
    loadOrganization();
    loadServices();
    loadStaff();
});

async function loadOrganization() {
    /**
     * Load the current organization details for this admin and update the UI.
     * Side effects: sets #orgName text content.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/admin/api/organization');
        const org = await response.json();
        document.getElementById('orgName').textContent = org.name || '';
    } catch (error) {
        console.error('Error loading organization:', error);
    }
}

function showTab(tabName) {
    // Switch visible tab and optionally load tab-specific data.
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');

    if (event && event.target) event.target.classList.add('active');
    document.getElementById(`${tabName}Tab`).style.display = 'block';

    if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// Services Management
async function loadServices() {
    /**
     * Load services for this organization and render them in the services table.
     * Side effects: updates `currentServices` and DOM element #servicesBody.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/admin/api/services');
        currentServices = await response.json();

        const tbody = document.getElementById('servicesBody');
        tbody.innerHTML = currentServices.map(service => `
            <tr>
                <td>${service.name}</td>
                <td>${service.counter_number}</td>
                <td>${service.avg_service_time} min</td>
                <td><span class="status-badge ${service.is_active ? 'status-done' : 'status-skipped'}">
                    ${service.is_active ? 'Active' : 'Inactive'}
                </span></td>
                <td>
                    <button onclick="editService(${service.id})" class="btn btn-primary">Edit</button>
                    <button onclick="deleteService(${service.id})" class="btn btn-danger">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function showServiceForm() {
    /**
     * Show blank form for creating a new service and set default values.
     */
    document.getElementById('serviceForm').style.display = 'block';
    document.getElementById('formTitle').textContent = 'Add Service';
    document.getElementById('serviceId').value = '';
    document.getElementById('serviceName').value = '';
    document.getElementById('counterNumber').value = '';
    document.getElementById('avgTime').value = '10';
}

function editService(id) {
    /**
     * Populate the service form with an existing service for editing.
     * @param {number} id - service id to edit
     */
    const service = currentServices.find(s => s.id === id);
    if (service) {
        document.getElementById('serviceForm').style.display = 'block';
        document.getElementById('formTitle').textContent = 'Edit Service';
        document.getElementById('serviceId').value = service.id;
        document.getElementById('serviceName').value = service.name;
        document.getElementById('counterNumber').value = service.counter_number;
        document.getElementById('avgTime').value = service.avg_service_time;
    }
}

async function saveService() {
    /**
     * Create or update a service. Reads form inputs and POST/PUTs JSON to the API.
     * On success hides the form and refreshes services table.
     * @returns {Promise<void>}
     */
    const id = document.getElementById('serviceId').value;
    const data = {
        name: document.getElementById('serviceName').value,
        counter_number: document.getElementById('counterNumber').value,
        avg_service_time: parseInt(document.getElementById('avgTime').value)
    };

    try {
        const url = id ? `/admin/api/services/${id}` : '/admin/api/services';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            cancelForm();
            loadServices();
        }
    } catch (error) {
        console.error('Error saving service:', error);
    }
}

async function deleteService(id) {
    /**
     * Delete a service after user confirmation and refresh the services list.
     * @param {number} id - service id to delete
     * @returns {Promise<void>}
     */
    if (!confirm('Delete this service?')) return;

    try {
        const response = await fetch(`/admin/api/services/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadServices();
        }
    } catch (error) {
        console.error('Error deleting service:', error);
    }
}

function cancelForm() {
    /**
     * Hide the service form without applying changes.
     */
    document.getElementById('serviceForm').style.display = 'none';
}

// Staff Management
async function loadStaff() {
    /**
     * Load staff members and render them into the staff table using currentServices to
     * resolve their assigned service names.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/admin/api/staff');
        const staff = await response.json();

        const tbody = document.getElementById('staffBody');
        tbody.innerHTML = staff.map(member => {
            const service = currentServices.find(s => s.id === member.service_id);
            return `
                <tr>
                    <td>${member.username}</td>
                    <td>${service ? service.name : 'Unassigned'}</td>
                    <td>
                        <button onclick="editStaff(${member.id})" class="btn btn-primary">Edit</button>
                        <button onclick="deleteStaff(${member.id})" class="btn btn-danger">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading staff:', error);
    }
}

function showStaffForm() {
    /**
     * Show blank staff form and populate the service dropdown using `currentServices`.
     */
    document.getElementById('staffForm').style.display = 'block';
    document.getElementById('staffId').value = '';
    document.getElementById('staffUsername').value = '';
    document.getElementById('staffPassword').value = '';

    const select = document.getElementById('staffService');
    select.innerHTML = '<option value="">Select Service</option>' +
        currentServices.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
}

function editStaff(id) {
    // For simplicity, just allow reassigning service
    showStaffForm();
    document.getElementById('staffId').value = id;
    document.getElementById('staffUsername').disabled = true;
}

async function saveStaff() {
    /**
     * Create or update a staff member. If updating, username input is disabled.
     * Sends JSON to server and refreshes staff list on success.
     * @returns {Promise<void>}
     */
    const id = document.getElementById('staffId').value;
    const data = {
        username: document.getElementById('staffUsername').value,
        password: document.getElementById('staffPassword').value,
        service_id: document.getElementById('staffService').value || null
    };

    try {
        const url = id ? `/admin/api/staff/${id}` : '/admin/api/staff';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            cancelStaffForm();
            loadStaff();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to save staff');
        }
    } catch (error) {
        console.error('Error saving staff:', error);
    }
}

async function deleteStaff(id) {
    /**
     * Delete a staff member after confirmation.
     * @param {number} id - staff id to delete
     * @returns {Promise<void>}
     */
    if (!confirm('Delete this staff member?')) return;

    try {
        const response = await fetch(`/admin/api/staff/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadStaff();
        }
    } catch (error) {
        console.error('Error deleting staff:', error);
    }
}

function cancelStaffForm() {
    /**
     * Hide staff form and re-enable username input.
     */
    document.getElementById('staffForm').style.display = 'none';
    document.getElementById('staffUsername').disabled = false;
}

// Analytics
async function loadAnalytics() {
    /**
     * Load analytics data (defaults to 7 days) and render analytics cards.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/admin/api/analytics?days=7');
        const data = await response.json();

        const container = document.getElementById('analyticsData');
        container.innerHTML = data.map(item => `
            <div class="analytics-card">
                <h3>${item.service_name}</h3>
                <div class="analytics-stats">
                    <div>
                        <span>${item.total_served}</span>
                        <p>Total Served</p>
                    </div>
                    <div>
                        <span>${item.avg_wait_time} min</span>
                        <p>Avg Wait Time</p>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}