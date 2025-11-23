// Initialize background script (works for both Chrome MV3 and Firefox MV2)
console.log('Background script starting...');

// Use browser API for Firefox compatibility (Chrome also supports it)
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// Keep service worker alive using persistent connections
let keepAliveConnections = new Set();

// Handle persistent connections from content scripts (keeps service worker alive)
browserAPI.runtime.onConnect.addListener((port) => {
    if (port.name === 'keepAlive') {
        keepAliveConnections.add(port);
        console.log('Keep-alive connection established. Active connections:', keepAliveConnections.size);
        
        port.onDisconnect.addListener(() => {
            keepAliveConnections.delete(port);
            console.log('Keep-alive connection closed. Active connections:', keepAliveConnections.size);
        });
        
        // Handle ping messages
        port.onMessage.addListener((msg) => {
            if (msg.action === 'ping') {
                // Connection is alive, do nothing
            }
        });
    }
});

// Also use alarms as backup (Chrome MV3 only)
if (browserAPI.alarms) {
    browserAPI.alarms.onAlarm.addListener((alarm) => {
        if (alarm.name === 'keepAlive') {
            console.log('Service worker keep-alive ping via alarm');
        }
    });
    
    // More frequent alarm as backup (every 2 minutes)
    browserAPI.alarms.create('keepAlive', { periodInMinutes: 2 });
    console.log('Keep-alive alarm set (backup)');
}

// Handle installation/update
browserAPI.runtime.onInstalled.addListener((details) => {
    console.log('Extension installed/updated:', details.reason);
    // Set up keep-alive alarm on install
    if (browserAPI.alarms) {
        browserAPI.alarms.create('keepAlive', { periodInMinutes: 4 });
    }
});

// Listen for messages from content scripts
browserAPI.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "fetch") {
        // Perform async fetch operation
        console.log('Background fetch:', msg.url, msg.options);
        fetch(msg.url, msg.options || {})
            .then(res => {
                console.log('Background fetch response:', res.status, res.statusText);
                if (!res.ok) {
                    // Try to parse error response, fallback to status text
                    return res.text()
                        .then(text => {
                            console.log('Background fetch error response text:', text);
                            try {
                                const err = JSON.parse(text);
                                return { error: err.error || err.message || `HTTP ${res.status}: Request failed` };
                            } catch {
                                return { error: `HTTP ${res.status}: ${res.statusText}${text ? ` - ${text}` : ''}` };
                            }
                        });
                }
                // Try to parse JSON response
                return res.text()
                    .then(text => {
                        try {
                            const data = JSON.parse(text);
                            return { data };
                        } catch {
                            // If not JSON, return text as data
                            return { data: text };
                        }
                    });
            })
            .then(result => {
                console.log('Background fetch result:', result);
                sendResponse(result);
            })
            .catch(err => {
                console.error('Background fetch error:', err);
                sendResponse({ error: err.message || err.toString() });
            });
        
        // Return true to indicate we will send a response asynchronously
        return true;
    }
    
    // Return false for other messages we don't handle
    return false;
});

