// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadOverview();
    setupFormHandlers();
});

// Tab navigation
function showTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    // Load data for the tab
    switch(tabName) {
        case 'overview':
            loadOverview();
            break;
        case 'organizations':
            loadOrganizations();
            break;
        case 'services':
            loadServices();
            break;
        case 'providers':
            loadProviders();
            break;
    }
}

// Load overview analytics
async function loadOverview() {
    try {
        const response = await fetch('/admin/api/analytics/overview');
        const data = await response.json();
        
        document.getElementById('totalTicketsToday').textContent = data.total_tickets_today;
        document.getElementById('completedToday').textContent = data.completed_today;
        document.getElementById('activeNow').textContent = data.active_now;
        document.getElementById('avgWaitTime').textContent = data.average_wait_time + 'm';
        
        // Load service analytics
        const servicesResponse = await fetch('/admin/api/analytics/services');
        const services = await servicesResponse.json();
        
        const container = document.getElementById('serviceAnalytics');
        if (services.length === 0) {
            container.innerHTML = '<p>No service data available</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Service</th>
                            <th>Organization</th>
                            <th>Total Today</th>
                            <th>Completed</th>
                            <th>Waiting Now</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${services.map(s => `
                            <tr>
                                <td>${s.service_name}</td>
                                <td>${s.organization}</td>
                                <td>${s.total_today}</td>
                                <td>${s.completed}</td>
                                <td>${s.waiting_now}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Organizations
async function loadOrganizations() {
    try {
        const response = await fetch('/admin/api/organizations');
        const orgs = await response.json();
        
        const container = document.getElementById('orgsList');
        if (orgs.length === 0) {
            container.innerHTML = '<p>No organizations yet</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Location</th>
                            <th>Phone</th>
                            <th>Services</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${orgs.map(org => `
                            <tr>
                                <td>${org.name}</td>
                                <td>${org.type || '-'}</td>
                                <td>${org.location || '-'}</td>
                                <td>${org.contact_phone || '-'}</td>
                                <td>${org.services_count}</td>
                                <td>${org.is_active ? '✓ Active' : '✗ Inactive'}</td>
                                <td class="action-btns">
                                    <button class="btn-edit" onclick="editOrg(${org.id})">Edit</button>
                                    <button class="btn-delete" onclick="deleteOrg(${org.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

function showOrgModal() {
    document.getElementById('orgModalTitle').textContent = 'Add Organization';
    document.getElementById('orgForm').reset();
    document.getElementById('orgId').value = '';
    document.getElementById('orgModal').classList.add('active');
}

async function editOrg(id) {
    const response = await fetch('/admin/api/organizations');
    const orgs = await response.json();
    const org = orgs.find(o => o.id === id);
    
    if (org) {
        document.getElementById('orgModalTitle').textContent = 'Edit Organization';
        document.getElementById('orgId').value = org.id;
        document.getElementById('orgName').value = org.name;
        document.getElementById('orgType').value = org.type || '';
        document.getElementById('orgLocation').value = org.location || '';
        document.getElementById('orgPhone').value = org.contact_phone || '';
        document.getElementById('orgModal').classList.add('active');
    }
}

async function deleteOrg(id) {
    if (!confirm('Are you sure you want to delete this organization?')) return;
    
    try {
        const response = await fetch(`/admin/api/organizations/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            loadOrganizations();
        } else {
            alert('Failed to delete organization');
        }
    } catch (error) {
        console.error('Error deleting organization:', error);
        alert('Network error');
    }
}

// Services
async function loadServices() {
    try {
        const response = await fetch('/admin/api/services');
        const services = await response.json();
        
        const container = document.getElementById('servicesList');
        if (services.length === 0) {
            container.innerHTML = '<p>No services yet</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Service Name</th>
                            <th>Organization</th>
                            <th>Counter</th>
                            <th>Est. Time (min)</th>
                            <th>Queue Length</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${services.map(s => `
                            <tr>
                                <td>${s.name}</td>
                                <td>${s.organization_name}</td>
                                <td>${s.counter_number || '-'}</td>
                                <td>${s.estimated_service_time}</td>
                                <td>${s.current_queue_length}</td>
                                <td>${s.is_active ? '✓ Active' : '✗ Inactive'}</td>
                                <td class="action-btns">
                                    <button class="btn-edit" onclick="editService(${s.id})">Edit</button>
                                    <button class="btn-delete" onclick="deleteService(${s.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

async function showServiceModal() {
    // Load organizations for dropdown
    const response = await fetch('/admin/api/organizations');
    const orgs = await response.json();
    
    const select = document.getElementById('serviceOrgId');
    select.innerHTML = orgs.map(org => 
        `<option value="${org.id}">${org.name}</option>`
    ).join('');
    
    document.getElementById('serviceModalTitle').textContent = 'Add Service';
    document.getElementById('serviceForm').reset();
    document.getElementById('serviceId').value = '';
    document.getElementById('serviceModal').classList.add('active');
}

async function editService(id) {
    const response = await fetch('/admin/api/services');
    const services = await response.json();
    const service = services.find(s => s.id === id);
    
    if (service) {
        await showServiceModal();
        document.getElementById('serviceModalTitle').textContent = 'Edit Service';
        document.getElementById('serviceId').value = service.id;
        document.getElementById('serviceOrgId').value = service.organization_id;
        document.getElementById('serviceName').value = service.name;
        document.getElementById('serviceCounter').value = service.counter_number || '';
        document.getElementById('serviceTime').value = service.estimated_service_time;
    }
}

async function deleteService(id) {
    if (!confirm('Are you sure you want to delete this service?')) return;
    
    try {
        const response = await fetch(`/admin/api/services/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            loadServices();
        } else {
            alert('Failed to delete service');
        }
    } catch (error) {
        console.error('Error deleting service:', error);
        alert('Network error');
    }
}

// Service Providers
async function loadProviders() {
    try {
        const response = await fetch('/admin/api/providers');
        const providers = await response.json();
        
        const container = document.getElementById('providersList');
        if (providers.length === 0) {
            container.innerHTML = '<p>No service providers yet</p>';
        } else {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Full Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Service</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${providers.map(p => `
                            <tr>
                                <td>${p.full_name}</td>
                                <td>${p.username}</td>
                                <td>${p.email}</td>
                                <td>${p.phone || '-'}</td>
                                <td>${p.service_name}</td>
                                <td>${p.is_active ? '✓ Active' : '✗ Inactive'}</td>
                                <td class="action-btns">
                                    <button class="btn-edit" onclick="editProvider(${p.id})">Edit</button>
                                    <button class="btn-delete" onclick="deleteProvider(${p.id})">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        console.error('Error loading providers:', error);
    }
}

async function showProviderModal() {
    // Load services for dropdown
    const response = await fetch('/admin/api/services');
    const services = await response.json();
    
    const select = document.getElementById('providerServiceId');
    select.innerHTML = services.map(s => 
        `<option value="${s.id}">${s.name} - ${s.organization_name}</option>`
    ).join('');
    
    document.getElementById('providerModalTitle').textContent = 'Add Staff Member';
    document.getElementById('providerForm').reset();
    document.getElementById('providerId').value = '';
    document.getElementById('providerPassword').required = true;
    document.getElementById('providerModal').classList.add('active');
}

async function editProvider(id) {
    const response = await fetch('/admin/api/providers');
    const providers = await response.json();
    const provider = providers.find(p => p.id === id);
    
    if (provider) {
        await showProviderModal();
        document.getElementById('providerModalTitle').textContent = 'Edit Staff Member';
        document.getElementById('providerId').value = provider.id;
        document.getElementById('providerName').value = provider.full_name;
        document.getElementById('providerUsername').value = provider.username;
        document.getElementById('providerEmail').value = provider.email;
        document.getElementById('providerPhone').value = provider.phone || '';
        document.getElementById('providerServiceId').value = provider.service_id;
        document.getElementById('providerPassword').required = false;
        document.getElementById('providerPassword').value = '';
    }
}

async function deleteProvider(id) {
    if (!confirm('Are you sure you want to delete this provider?')) return;
    
    try {
        const response = await fetch(`/admin/api/providers/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            loadProviders();
        } else {
            alert('Failed to delete provider');
        }
    } catch (error) {
        console.error('Error deleting provider:', error);
        alert('Network error');
    }
}

// Modal functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Form handlers
function setupFormHandlers() {
    // Organization form
    document.getElementById('orgForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('orgId').value;
        const data = {
            name: document.getElementById('orgName').value,
            type: document.getElementById('orgType').value,
            location: document.getElementById('orgLocation').value,
            contact_phone: document.getElementById('orgPhone').value
        };
        
        try {
            const url = id ? `/admin/api/organizations/${id}` : '/admin/api/organizations';
            const method = id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                closeModal('orgModal');
                loadOrganizations();
            } else {
                alert('Failed to save organization');
            }
        } catch (error) {
            console.error('Error saving organization:', error);
            alert('Network error');
        }
    });
    
    // Service form
    document.getElementById('serviceForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('serviceId').value;
        const data = {
            organization_id: parseInt(document.getElementById('serviceOrgId').value),
            name: document.getElementById('serviceName').value,
            counter_number: document.getElementById('serviceCounter').value,
            estimated_service_time: parseInt(document.getElementById('serviceTime').value)
        };
        
        try {
            const url = id ? `/admin/api/services/${id}` : '/admin/api/services';
            const method = id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                closeModal('serviceModal');
                loadServices();
            } else {
                alert('Failed to save service');
            }
        } catch (error) {
            console.error('Error saving service:', error);
            alert('Network error');
        }
    });
    
    // Provider form
    document.getElementById('providerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = document.getElementById('providerId').value;
        const data = {
            full_name: document.getElementById('providerName').value,
            username: document.getElementById('providerUsername').value,
            email: document.getElementById('providerEmail').value,
            phone: document.getElementById('providerPhone').value,
            service_id: parseInt(document.getElementById('providerServiceId').value)
        };
        
        const password = document.getElementById('providerPassword').value;
        if (password) {
            data.password = password;
        }
        
        try {
            const url = id ? `/admin/api/providers/${id}` : '/admin/api/providers';
            const method = id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                closeModal('providerModal');
                loadProviders();
            } else {
                alert('Failed to save provider');
            }
        } catch (error) {
            console.error('Error saving provider:', error);
            alert('Network error');
        }
    });
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}