// Initialize background service worker
console.log('Background service worker initialized');

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
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

// Keep service worker alive by listening to events
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed/updated');
});
