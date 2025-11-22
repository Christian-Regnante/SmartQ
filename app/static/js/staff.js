document.addEventListener('DOMContentLoaded', () => {
    loadServiceInfo();
    loadQueue();
    loadStats();
    
    setInterval(loadQueue, 5000);
    setInterval(loadStats, 10000);
});

async function loadServiceInfo() {
    try {
        const response = await fetch('/staff/api/service-info');
        const service = await response.json();
        document.getElementById('serviceName').textContent = service.name;
    } catch (error) {
        console.error('Error loading service info:', error);
    }
}

async function loadQueue() {
    try {
        const response = await fetch('/staff/api/queue');
        const queue = await response.json();
        
        const tbody = document.getElementById('queueBody');
        tbody.innerHTML = queue.map(item => `
            <tr class="status-${item.status}">
                <td><strong>${item.queue_number}</strong></td>
                <td>${item.phone_number}</td>
                <td><span class="status-badge status-${item.status}">${item.status}</span></td>
                <td>${new Date(item.created_at).toLocaleTimeString()}</td>
                <td>
                    ${item.status === 'serving' ? `
                        <button onclick="markDone(${item.id})" class="btn btn-primary">Done</button>
                    ` : ''}
                    ${!item.status === 'waiting' ? `
                        <button onclick="skip(${item.id})" class="btn btn-danger">Skip</button>
                    ` : ''}
                    ${item.status === 'serving' ? `
                        <button onclick="skip(${item.id})" class="btn btn-danger">Skip</button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
        
        const serving = queue.find(item => item.status === 'serving');
        const currentDiv = document.getElementById('currentServing');
        if (serving) {
            currentDiv.textContent = `Currently Serving: ${serving.queue_number}`;
        } else {
            currentDiv.textContent = 'No one being served';
        }
    } catch (error) {
        console.error('Error loading queue:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/staff/api/stats');
        const stats = await response.json();
        
        document.getElementById('servedToday').textContent = stats.served_today;
        document.getElementById('avgWait').textContent = stats.avg_wait_time;
        document.getElementById('waiting').textContent = stats.currently_waiting;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function callNext() {
    try {
        const response = await fetch('/staff/api/call-next', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadQueue();
            loadStats();
        } else {
            alert(data.message || 'No one waiting');
        }
    } catch (error) {
        console.error('Error calling next:', error);
    }
}

async function markDone(itemId) {
    try {
        const response = await fetch(`/staff/api/mark-done/${itemId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadQueue();
            loadStats();
        }
    } catch (error) {
        console.error('Error marking done:', error);
    }
}

async function skip(itemId) {
    if (!confirm('Skip this client?')) return;
    
    try {
        const response = await fetch(`/staff/api/skip/${itemId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadQueue();
            loadStats();
        }
    } catch (error) {
        console.error('Error skipping:', error);
    }
}