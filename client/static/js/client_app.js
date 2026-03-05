// Client Simulator JavaScript

function addToResponse(message, isError = false) {
    const responseArea = document.getElementById('responseArea');
    const timestamp = new Date().toLocaleTimeString();
    const color = isError ? '#ff6b6b' : '#69db7e';
    
    const entry = document.createElement('div');
    entry.innerHTML = `<span style="color: #888;">[${timestamp}]</span> <span style="color: ${color};">${message}</span>`;
    
    responseArea.appendChild(entry);
    responseArea.scrollTop = responseArea.scrollHeight;
}

async function sendRequest(tamper = false) {
    const citizenId = document.getElementById('citizenId').value;
    
    addToResponse(`📤 Sending ${tamper ? 'TAMPERED' : 'VALID'} request for citizen ${citizenId}...`);
    
    try {
        const response = await fetch('/api/send-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                citizen_id: citizenId,
                tamper: tamper
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const statusCode = data.response_status;
            const isAccepted = statusCode === 200;
            
            if (isAccepted) {
                addToResponse(`✅ ACCEPTED! Status: ${statusCode}`);
                if (data.response_data.data) {
                    addToResponse(`   Citizen: ${data.response_data.data.name}, Sector: ${data.response_data.data.sector}`);
                }
            } else {
                addToResponse(`❌ REJECTED! Status: ${statusCode}`, true);
                if (data.response_data.message) {
                    addToResponse(`   Reason: ${data.response_data.message}`, true);
                }
            }
            
            addToResponse(`   Signature: ${data.request_details.signature}`);
            addToResponse(`   Nonce: ${data.request_details.nonce}`);
        }
        
    } catch (error) {
        addToResponse(`❌ Error: ${error.message}`, true);
    }
    
    updateStats();
}

async function replayRequest() {
    addToResponse(`🔄 Attempting replay attack...`);
    
    try {
        const response = await fetch('/api/replay-request', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const statusCode = data.response_status;
            
            if (statusCode === 200) {
                addToResponse(`⚠️ REPLAY SUCCEEDED! (This should NOT happen!)`, true);
            } else {
                addToResponse(`✅ REPLAY DETECTED! Status: ${statusCode}`, false);
                if (data.response_data.message) {
                    addToResponse(`   Reason: ${data.response_data.message}`, false);
                }
            }
        }
        
    } catch (error) {
        addToResponse(`❌ Error: ${error.message}`, true);
    }
    
    updateStats();
}

async function updateStats() {
    try {
        const response = await fetch('/api/captured-requests');
        const data = await response.json();
        document.getElementById('requestCount').textContent = data.count;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update stats every 5 seconds
setInterval(updateStats, 5000);