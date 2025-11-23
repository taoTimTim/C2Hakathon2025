chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "fetch") {
        fetch(msg.url, msg.options || {})
            .then(res => res.json())
            .then(data => sendResponse({ data }))
            .catch(err => sendResponse({ error: err.toString() }));
        return true; // keeps message port open
    }
});
