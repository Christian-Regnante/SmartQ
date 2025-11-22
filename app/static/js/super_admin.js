let currentOrgs = [];

document.addEventListener('DOMContentLoaded', () => {
    loadOverview();
    loadOrganizations();
});

async function loadOverview() {
    /**
     * Fetch aggregated counts for dashboard overview and populate the summary cards.
     * Side effects: updates DOM elements #totalOrgs, #totalAdmins, #totalStaff, #totalServices.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/super-admin/api/overview');
        const data = await response.json();

        document.getElementById('totalOrgs').textContent = data.total_organizations;
        document.getElementById('totalAdmins').textContent = data.total_admins;
        document.getElementById('totalStaff').textContent = data.total_staff;
        document.getElementById('totalServices').textContent = data.total_services;
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

function showTab(tabName) {
    // Switch visible tab: remove active state from all and hide their content
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');

    // `event` is expected to be the click event from the element that triggered this function.
    // Caller must ensure `showTab` is invoked from an event handler (e.g. onclick="showTab('admins')").
    if (event && event.target) event.target.classList.add('active');
    document.getElementById(`${tabName}Tab`).style.display = 'block';

    // Load additional data when opening specific tabs
    if (tabName === 'admins') {
        loadAdmins();
    }
}

// Organizations Management
async function loadOrganizations() {
    /**
     * Load organizations for management table and cache them in `currentOrgs`.
     * Side effects: sets `currentOrgs` and renders rows into #orgsBody.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/super-admin/api/organizations');
        currentOrgs = await response.json();

        const tbody = document.getElementById('orgsBody');
        tbody.innerHTML = currentOrgs.map(org => `
            <tr>
                <td><strong>${org.name}</strong></td>
                <td>${org.location || '-'}</td>
                <td>${org.contact || '-'}</td>
                <td>${org.admin_count}</td>
                <td>${org.service_count}</td>
                <td>${org.staff_count}</td>
                <td>
                    <button onclick="editOrganization(${org.id})" class="btn btn-primary">Edit</button>
                    <button onclick="deleteOrganization(${org.id})" class="btn btn-danger">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

function showOrgForm() {
    /**
     * Show the organization add form and clear inputs for a fresh create.
     * Side effects: manipulates #orgForm inputs and title.
     */
    document.getElementById('orgForm').style.display = 'block';
    document.getElementById('orgFormTitle').textContent = 'Add Organization';
    document.getElementById('orgId').value = '';
    document.getElementById('orgName').value = '';
    document.getElementById('orgLocation').value = '';
    document.getElementById('orgContact').value = '';
}

function editOrganization(id) {
    /**
     * Populate the organization form with existing org values for editing.
     * @param {number} id - organization id to edit
     */
    const org = currentOrgs.find(o => o.id === id);
    if (org) {
        document.getElementById('orgForm').style.display = 'block';
        document.getElementById('orgFormTitle').textContent = 'Edit Organization';
        document.getElementById('orgId').value = org.id;
        document.getElementById('orgName').value = org.name;
        document.getElementById('orgLocation').value = org.location || '';
        document.getElementById('orgContact').value = org.contact || '';
    }
}

async function saveOrganization() {
    /**
     * Create or update an organization based on whether #orgId has a value.
     * Sends JSON to server and refreshes the table and overview on success.
     * @returns {Promise<void>}
     */
    const id = document.getElementById('orgId').value;
    const data = {
        name: document.getElementById('orgName').value,
        location: document.getElementById('orgLocation').value,
        contact: document.getElementById('orgContact').value
    };

    try {
        const url = id ? `/super-admin/api/organizations/${id}` : '/super-admin/api/organizations';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            cancelOrgForm();
            loadOrganizations();
            loadOverview();
        }
    } catch (error) {
        console.error('Error saving organization:', error);
    }
}

async function deleteOrganization(id) {
    /**
     * Delete an organization by id after user confirmation.
     * Side effects: removes org server-side, then refreshes list and overview.
     * @param {number} id - id of organization to delete
     * @returns {Promise<void>}
     */
    if (!confirm('Delete this organization? This will also delete all related services and staff.')) return;

    try {
        const response = await fetch(`/super-admin/api/organizations/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadOrganizations();
            loadOverview();
        }
    } catch (error) {
        console.error('Error deleting organization:', error);
    }
}

function cancelOrgForm() {
    /**
     * Hide the organization form without saving changes.
     */
    document.getElementById('orgForm').style.display = 'none';
}

// Admins Management
async function loadAdmins() {
    /**
     * Load admin users and render them into the admins table.
     * Side effects: updates DOM in #adminsBody.
     * @returns {Promise<void>}
     */
    try {
        const response = await fetch('/super-admin/api/admins');
        const admins = await response.json();

        const tbody = document.getElementById('adminsBody');
        tbody.innerHTML = admins.map(admin => `
            <tr>
                <td><strong>${admin.username}</strong></td>
                <td>${admin.organization_name}</td>
                <td>
                    <button onclick="editAdmin(${admin.id})" class="btn btn-primary">Edit</button>
                    <button onclick="deleteAdmin(${admin.id})" class="btn btn-danger">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading admins:', error);
    }
}

function showAdminForm() {
    /**
     * Display admin creation form and populate organization dropdown from cached `currentOrgs`.
     */
    document.getElementById('adminForm').style.display = 'block';
    document.getElementById('adminId').value = '';
    document.getElementById('adminUsername').value = '';
    document.getElementById('adminPassword').value = '';

    const select = document.getElementById('adminOrg');
    select.innerHTML = '<option value="">Select Organization</option>' +
        currentOrgs.map(o => `<option value="${o.id}">${o.name}</option>`).join('');
}

function editAdmin(id) {
    showAdminForm();
    document.getElementById('adminId').value = id;
    document.getElementById('adminUsername').disabled = true;
    document.getElementById('adminPassword').placeholder = 'Leave empty to keep current';
}

async function saveAdmin() {
    /**
     * Create or update an admin account. If updating, keep username disabled.
     * Sends JSON to server and refreshes admins and overview after success.
     * @returns {Promise<void>}
     */
    const id = document.getElementById('adminId').value;
    const data = {
        username: document.getElementById('adminUsername').value,
        password: document.getElementById('adminPassword').value,
        organization_id: document.getElementById('adminOrg').value || null
    };

    try {
        const url = id ? `/super-admin/api/admins/${id}` : '/super-admin/api/admins';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            cancelAdminForm();
            loadAdmins();
            loadOverview();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to save admin');
        }
    } catch (error) {
        console.error('Error saving admin:', error);
    }
}

async function deleteAdmin(id) {
    /**
     * Delete an admin account after confirmation and refresh lists.
     * @param {number} id - admin id to delete
     * @returns {Promise<void>}
     */
    if (!confirm('Delete this admin?')) return;

    try {
        const response = await fetch(`/super-admin/api/admins/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadAdmins();
            loadOverview();
        }
    } catch (error) {
        console.error('Error deleting admin:', error);
    }
}

function cancelAdminForm() {
    /**
     * Hide the admin form and re-enable username input.
     */
    document.getElementById('adminForm').style.display = 'none';
    document.getElementById('adminUsername').disabled = false;
}