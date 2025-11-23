// ===========================================================
// Canvas Social Spaces Extension - Full Dashboard Logic
// ===========================================================

const API_RECOMMEND = 'http://127.0.0.1:5000/recommend';
const API_ALL_ITEMS = 'http://127.0.0.1:5000/items';

console.log("UBC Social Spaces: Extension Loaded.");

initExtension();

function initExtension() {
    const globalNav = document.getElementById('menu');
    if (!globalNav) return;
    if (document.getElementById('ubc-clubs-nav-item')) return;

    const navItem = document.createElement('li');
    navItem.id = 'ubc-clubs-nav-item';
    navItem.className = 'ic-app-header__menu-list-item'; 

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

    navItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTray();
    });

    if (globalNav.childNodes.length > 6) {
        globalNav.insertBefore(navItem, globalNav.childNodes[6]);
    } else {
        globalNav.appendChild(navItem);
    }
}

async function toggleTray() {
    let tray = document.getElementById('ubc-clubs-tray');
    if (tray) {
        tray.classList.toggle('tray-open');
        return;
    }

    // Load HTML
    const url = chrome.runtime.getURL('canvas_connect.html');
    const response = await fetch(url);
    const html = await response.text();

    const trayContainer = document.createElement('div');
    trayContainer.id = 'ubc-clubs-tray-container';
    trayContainer.innerHTML = html;
    document.body.appendChild(trayContainer);

    // Close Handler
    document.getElementById('ubc-tray-close').addEventListener('click', () => {
        document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
    });

    // Logic: Check if First Time User
    const hasOnboarded = localStorage.getItem('ubc_social_onboarded');
    
    if (hasOnboarded === 'true') {
        showDashboard();
    } else {
        showOnboarding();
    }

    setupEventHandlers();

    setTimeout(() => {
        document.getElementById('ubc-clubs-tray').classList.add('tray-open');
    }, 50);
}

function setupEventHandlers() {
    // 1. Onboarding Submit
    document.getElementById('ai-submit-btn').addEventListener('click', handleOnboardingSubmit);

    // 2. Redo Onboarding Button (in Clubs tab)
    document.getElementById('redo-onboarding-btn').addEventListener('click', () => {
        localStorage.removeItem('ubc_social_onboarded');
        showOnboarding();
    });

    // 3. Tab Navigation
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // UI Toggle
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.remove('active');
                t.style.borderBottom = 'none';
                t.style.background = 'none';
            });
            tab.classList.add('active');
            tab.style.borderBottom = '2px solid #0374B5';
            tab.style.background = 'white';

            // Content Toggle
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            document.getElementById(tab.dataset.target).style.display = 'block';
        });
    });
}

// --- VIEW SWITCHING LOGIC ---

function showOnboarding() {
    document.getElementById('view-onboarding').style.display = 'block';
    document.getElementById('view-dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('view-onboarding').style.display = 'none';
    document.getElementById('view-dashboard').style.display = 'flex';
    
    // Load Data for Dashboard
    loadSchoolFeed();
    loadAllClubs();
    loadGroups();
}

// --- ONBOARDING LOGIC ---

async function handleOnboardingSubmit() {
    const btn = document.getElementById('ai-submit-btn');
    btn.innerText = "Thinking...";
    
    // 1. Get Data
    const year = document.getElementById('ai-year').value;
    const classes = document.getElementById('ai-classes').value.split(',');
    const interests = document.getElementById('ai-interests').value;

    // 2. Call AI
    try {
        const res = await fetch(API_RECOMMEND, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({year, classes, interests})
        });
        const data = await res.json();
        
        // 3. Render Results below form
        renderAIResults(data);
        
        // 4. Change Button to "Enter Dashboard"
        btn.innerText = "Go to Dashboard ->";
        btn.onclick = () => {
            localStorage.setItem('ubc_social_onboarded', 'true');
            showDashboard();
        };

    } catch (e) {
        console.error(e);
        alert("Backend error. Ensure Python is running.");
    }
}

function renderAIResults(items) {
    const area = document.getElementById('ai-results-area');
    area.innerHTML = '<h4>✨ Recommended for You</h4>';
    items.forEach(item => {
        area.innerHTML += createCardHTML(item, true);
    });
}

// --- DASHBOARD DATA LOADERS ---

async function loadAllClubs() {
    const container = document.getElementById('all-clubs-list');
    container.innerHTML = '<p>Loading directory...</p>';
    
    try {
        const res = await fetch(API_ALL_ITEMS);
        const items = await res.json();
        
        container.innerHTML = '';
        
        // Render all
        items.forEach(item => {
            container.innerHTML += createCardHTML(item);
        });

        // Simple Search Logic
        document.getElementById('club-search').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const cards = container.querySelectorAll('.dashboard-card');
            cards.forEach(card => {
                const text = card.innerText.toLowerCase();
                card.style.display = text.includes(term) ? 'block' : 'none';
            });
        });

    } catch (e) {
        container.innerHTML = '<p style="color:red">Failed to load directory.</p>';
    }
}

function loadSchoolFeed() {
    // Mock Data for School Feed
    const feed = document.getElementById('feed-posts');
    feed.innerHTML = `
        <div class="dashboard-card">
            <strong>🎓 UBC Student Union</strong>
            <p>Free coffee in the library today starting at 10 AM!</p>
            <small style="color:grey">1 hour ago</small>
        </div>
        <div class="dashboard-card">
            <strong>🚧 Campus Security</strong>
            <p>North parking lot is closed for maintenance.</p>
            <small style="color:grey">Yesterday</small>
        </div>
    `;
    
    // Populate Events from Backend (reusing item loader for category='Event')
    // For hackathon speed, we'll just fetch all items and filter for events
    fetch(API_ALL_ITEMS).then(res => res.json()).then(items => {
        const eventContainer = document.getElementById('feed-events');
        const events = items.filter(i => i.category === 'Event').slice(0, 3);
        eventContainer.innerHTML = '';
        events.forEach(ev => {
            eventContainer.innerHTML += `
                <div class="dashboard-card" style="border-left: 3px solid #f8d7da;">
                    <strong>${ev.name}</strong><br>
                    <small>${ev.description.substring(0, 60)}...</small>
                </div>
            `;
        });
    });
}

function loadGroups() {
    // Mock "Joined" Groups
    const joined = JSON.parse(localStorage.getItem('ubc_my_groups') || '[]');
    const container = document.getElementById('my-joined-chats');
    
    if (joined.length > 0) {
        container.innerHTML = '';
        joined.forEach(g => {
            container.innerHTML += `
                <div class="dashboard-card" style="display:flex; justify-content:space-between;">
                    <span>💬 ${g}</span>
                    <button style="background:green; color:white; border:none; border-radius:50%;">✓</button>
                </div>`;
        });
    }

    // Load Available Groups from Backend (Category = Group)
    fetch(API_ALL_ITEMS).then(res => res.json()).then(items => {
        const groupContainer = document.getElementById('available-group-chats');
        const groups = items.filter(i => i.category === 'Group');
        groupContainer.innerHTML = '';
        groups.forEach(g => {
            // Add Join Logic Button
            groupContainer.innerHTML += `
                <div class="dashboard-card">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>${g.name}</strong>
                        <button onclick="joinGroup('${g.name}')" style="cursor:pointer;">+ Join</button>
                    </div>
                    <p style="font-size:0.8em;">${g.description}</p>
                </div>
            `;
        });
    });
}

// Global function for the onclick handler above
window.joinGroup = function(groupName) {
    let joined = JSON.parse(localStorage.getItem('ubc_my_groups') || '[]');
    if (!joined.includes(groupName)) {
        joined.push(groupName);
        localStorage.setItem('ubc_my_groups', JSON.stringify(joined));
        alert(`Joined ${groupName}!`);
        loadGroups(); // Refresh UI
    } else {
        alert("You are already in this group.");
    }
};

// Helper: Generate HTML for a Item Card
function createCardHTML(item, showScore=false) {
    let tagColor = "#eee";
    if (item.category === "Club") tagColor = "#d1e7dd";
    if (item.category === "Event") tagColor = "#f8d7da";
    if (item.category === "Tech") tagColor = "#cff4fc";

    let contactLink = "";
    if (item.contact && item.contact.includes('http')) {
        contactLink = `<a href="${item.contact.split('|')[0].trim()}" target="_blank" style="font-size:0.8em;">🔗 Link</a>`;
    }

    return `
        <div class="dashboard-card">
            <div style="display:flex; justify-content:space-between;">
                <h4 style="margin:0;">${item.name}</h4>
                <span style="background:${tagColor}; padding:2px 8px; border-radius:10px; font-size:0.7em;">${item.category}</span>
            </div>
            <p style="font-size:0.85em; color:#444; margin:5px 0;">${item.description}</p>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                ${contactLink}
                ${showScore ? `<span style="color:green; font-weight:bold; font-size:0.8em;">${Math.round(item.match_score*100)}% Match</span>` : ''}
            </div>
        </div>
    `;
}