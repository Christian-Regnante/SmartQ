let serviceInfo = null;
let refreshInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadServiceInfo();
    loadStats();
    loadQueue();
    
    // Auto-refresh every 10 seconds
    refreshInterval = setInterval(() => {
        loadQueue();
        loadStats();
    }, 10000);
});

// Load service provider info
async function loadServiceInfo() {
    try {
        const response = await fetch('/staff/api/my-service');
        const data = await response.json();
        
        if (data.service_id) {
            serviceInfo = data;
            document.getElementById('serviceInfo').textContent = 
                `${data.service_name} - ${data.counter}`;
        }
    } catch (error) {
        console.error('Error loading service info:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/staff/api/stats');
        const data = await response.json();
        
        document.getElementById('servedToday').textContent = data.served_today;
        document.getElementById('waitingCount').textContent = data.waiting_count;
        document.getElementById('avgServiceTime').textContent = data.average_service_time + 'm';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load queue
async function loadQueue() {
    try {
        const response = await fetch('/staff/api/queue');
        const data = await response.json();
        
        // Update serving client
        const servingDiv = document.getElementById('servingClient');
        if (data.serving) {
            servingDiv.innerHTML = `
                <div class="serving-client">
                    <div class="queue-number">${data.serving.queue_number}</div>
                    <p>Phone: ***${data.serving.phone}</p>
                    <p>Since: ${data.serving.serving_since}</p>
                    <button class="primary-btn" style="margin-top: 15px;" onclick="completeService(${data.serving.id})">
                        ✓ Complete
                    </button>
                </div>
            `;
        } else {
            servingDiv.innerHTML = '<div class="serving-empty">No client being served</div>';
        }
        
        // Update waiting queue
        const queueDiv = document.getElementById('queueList');
        if (data.waiting.length === 0) {
            queueDiv.innerHTML = '<div class="serving-empty">No clients in queue</div>';
        } else {
            queueDiv.innerHTML = data.waiting.map(item => `
                <div class="queue-item">
                    <div class="queue-item-info">
                        <div class="queue-item-number">#${item.position} - ${item.queue_number}</div>
                        <div class="queue-item-meta">Phone: ***${item.phone} | Joined: ${item.created_at}</div>
                    </div>
                    <div class="queue-item-actions">
                        <button class="btn-skip" onclick="skipClient(${item.id})">Skip</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading queue:', error);
    }
}

// Call next client
async function callNext() {
    try {
        const response = await fetch('/staff/api/call-next', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadQueue();
            loadStats();
        } else {
            alert(data.error || 'Failed to call next client');
        }
    } catch (error) {
        console.error('Error calling next:', error);
        alert('Network error. Please try again.');
    }
}

// Complete service
async function completeService(itemId) {
    try {
        const response = await fetch(`/staff/api/complete/${itemId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadQueue();
            loadStats();
        } else {
            alert(data.error || 'Failed to complete service');
        }
    } catch (error) {
        console.error('Error completing service:', error);
        alert('Network error. Please try again.');
    }
}

// Skip client
async function skipClient(itemId) {
    if (!confirm('Are you sure you want to skip this client?')) {
        return;
    }
    
    try {
        const response = await fetch(`/staff/api/skip/${itemId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadQueue();
            loadStats();
        } else {
            alert(data.error || 'Failed to skip client');
        }
    } catch (error) {
        console.error('Error skipping client:', error);
        alert('Network error. Please try again.');
    }
}

// Refresh queue manually
function refreshQueue() {
    loadQueue();
    loadStats();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});