// ===========================================================
// Canvas Social Spaces Extension - Integrated AI Backend
// ===========================================================

// 1. Point to your local Python AI Service
const API_ENDPOINT = 'http://127.0.0.1:5000/recommend'; 

console.log("UBC Social Spaces: Extension Loaded.");

// Initialize the extension on load
initExtension();

function initExtension() {
    // 1. Find the Global Navigation Menu
    const globalNav = document.getElementById('menu');
    if (!globalNav) return;

    // 2. Prevent duplicate injection
    if (document.getElementById('ubc-clubs-nav-item')) return;

    // 3. Create the List Item (li) and Link (a)
    const navItem = document.createElement('li');
    navItem.id = 'ubc-clubs-nav-item';
    navItem.className = 'ic-app-header__menu-list-item'; 

    // Create the inner HTML (Using YOUR specific SVG and "Connect" text)
    navItem.innerHTML = `
        <a id="global_nav_clubs_link" href="#" class="ic-app-header__menu-list-link">
            <div class="menu-item-icon-container" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3">
                    <path d="M160-120q-33 0-56.5-23.5T80-200v-560q0-33 23.5-56.5T160-840h560q33 0 56.5 23.5T800-760v80h80v80h-80v80h80v80h-80v80h80v80h-80v80q0 33-23.5 56.5T720-120H160Zm0-80h560v-560H160v560Zm80-80h200v-160H240v160Zm240-280h160v-120H480v120Zm-240 80h200v-200H240v200Zm240 200h160v-240H480v240ZM160-760v560-560Z"/>
                </svg>
            </div>
            <div class="menu-item__text">Connect</div>
        </a>
    `;

    // 4. Add Click Event
    navItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTray();
    });

    // 5. Append to the menu (Using YOUR specific insertBefore logic)
    // Note: using childNodes[6] might be fragile if Canvas changes layout, but keeping as requested.
    if (globalNav.childNodes.length > 6) {
        globalNav.insertBefore(navItem, globalNav.childNodes[6]);
    } else {
        globalNav.appendChild(navItem); // Fallback
    }
}

async function toggleTray() {
    let tray = document.getElementById('ubc-clubs-tray');
    
    if (tray) {
        tray.classList.toggle('tray-open');
        return;
    }

    // --- STEP 1: Load the Tray HTML ---
    const url = chrome.runtime.getURL('canvas_connect.html');
    const response = await fetch(url);
    const html = await response.text();

    const trayContainer = document.createElement('div');
    trayContainer.id = 'ubc-clubs-tray-container';
    trayContainer.innerHTML = html;
    document.body.appendChild(trayContainer);

    // Close Button Logic
    document.getElementById('ubc-tray-close').addEventListener('click', () => {
        document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
    });

    // --- STEP 2: Render the Input Form ---
    // We do NOT fetch data immediately. We wait for user input.
    renderOnboardingForm();
    
    setTimeout(() => {
        document.getElementById('ubc-clubs-tray').classList.add('tray-open');
    }, 50);
}

/**
 * Renders the input form so the user can tell the AI who they are.
 */
function renderOnboardingForm() {
    const container = document.getElementById('ubc-clubs-list');
    
    container.innerHTML = `
        <div style="padding: 15px; background: #f5f5f5; border-radius: 8px;">
            <h3 style="margin-top:0;">Find Your Community</h3>
            <p style="font-size:0.9em; color:#666;">Tell us a bit about yourself to get AI recommendations.</p>
            
            <div style="margin-bottom: 10px;">
                <label style="display:block; font-weight:bold;">Year:</label>
                <select id="ai-year" style="width:100%; padding: 8px;">
                    <option value="1st Year">1st Year</option>
                    <option value="2nd Year">2nd Year</option>
                    <option value="3rd Year">3rd Year</option>
                    <option value="4th Year+">4th Year+</option>
                    <option value="Grad Student">Grad Student</option>
                </select>
            </div>

            <div style="margin-bottom: 10px;">
                <label style="display:block; font-weight:bold;">Classes:</label>
                <input type="text" id="ai-classes" placeholder="COSC 101, MATH 200" style="width:100%; padding: 8px;">
            </div>

            <div style="margin-bottom: 15px;">
                <label style="display:block; font-weight:bold;">Interests:</label>
                <textarea id="ai-interests" rows="3" placeholder="I like hiking, chess, and coding..." style="width:100%; padding: 8px;"></textarea>
            </div>

            <button id="ai-submit-btn" style="width:100%; background:#0374B5; color:white; padding:10px; border:none; border-radius:4px; cursor:pointer;">
                ✨ Find My Spaces
            </button>
        </div>
        <div id="ai-results-area" style="margin-top: 20px;"></div>
    `;

    // Attach listener to the new button
    document.getElementById('ai-submit-btn').addEventListener('click', fetchRecommendations);
}

/**
 * Gathers input, calls Python API, and renders results.
 */
async function fetchRecommendations() {
    const resultsArea = document.getElementById('ai-results-area');
    const btn = document.getElementById('ai-submit-btn');
    
    // Visual Loading State
    btn.innerText = "Thinking...";
    btn.disabled = true;
    resultsArea.innerHTML = '<p style="text-align:center; color:#666;">🤖 AI is analyzing campus spaces...</p>';

    // 1. Gather Data
    const year = document.getElementById('ai-year').value;
    const classesRaw = document.getElementById('ai-classes').value;
    const interests = document.getElementById('ai-interests').value;

    const payload = {
        year: year,
        classes: classesRaw.split(',').map(s => s.trim()), // Convert "A, B" -> ["A", "B"]
        interests: interests
    };

    try {
        // 2. Send POST Request to Python Backend
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        // 3. Render Results
        resultsArea.innerHTML = ''; // Clear loading message
        btn.innerText = "✨ Find My Spaces";
        btn.disabled = false;

        if (data.length === 0) {
            resultsArea.innerHTML = '<p>No matches found. Try adding more details about your hobbies!</p>';
            return;
        }

        data.forEach(item => {
            // Determine Color Tag based on Category
            let tagColor = "#eee";
            if (item.category === "Club") tagColor = "#d1e7dd"; // Greenish
            if (item.category === "Event") tagColor = "#f8d7da"; // Reddish
            if (item.category === "Tech") tagColor = "#cff4fc"; // Blueish

            // Logic for Contact Button
            let contactBtn = '';
            if (item.contact) {
                if (item.contact.includes('http')) {
                    contactBtn = `<a href="${item.contact.split('|')[0].trim()}" target="_blank" style="display:inline-block; margin-top:5px; color:#0374B5; text-decoration:none; font-weight:bold;">🔗 Visit Page</a>`;
                } else {
                    contactBtn = `<span style="display:block; margin-top:5px; font-size:0.85em; color:#555;">📧 ${item.contact}</span>`;
                }
            }

            const card = document.createElement('div');
            card.className = 'club-card';
            // Use inline styles to avoid needing external CSS updates
            card.style.border = "1px solid #ddd";
            card.style.marginBottom = "15px";
            card.style.padding = "15px";
            card.style.borderRadius = "8px";
            card.style.backgroundColor = "white";
            card.style.boxShadow = "0 2px 4px rgba(0,0,0,0.05)";

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <h4 style="margin:0 0 5px 0; color:#2D3B45;">${item.name}</h4>
                    <span style="background:${tagColor}; padding:2px 8px; border-radius:12px; font-size:0.7em;">${item.category}</span>
                </div>
                
                <p style="font-size:0.9em; color:#444; margin: 5px 0;">${item.description}</p>
                
                ${contactBtn}
                
                <div style="margin-top:8px; font-size:0.8em; color:green; font-weight:bold;">
                    Match Score: ${Math.round(item.match_score * 100)}%
                </div>
            `;
            resultsArea.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        resultsArea.innerHTML = `
            <div style="color:red; background:#fff0f0; padding:10px; border-radius:5px;">
                <strong>Connection Error:</strong> Could not reach AI server.<br>
                <small>Make sure <code>python recommendation_service.py</code> is running!</small>
            </div>
        `;
        btn.innerText = "✨ Find My Spaces";
        btn.disabled = false;
    }
}