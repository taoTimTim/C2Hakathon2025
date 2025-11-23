// ===========================================================
// ROBUST VERSION - Left Tray & Full Screen Dashboard
// ===========================================================

const API_RECOMMEND = 'http://127.0.0.1:5000/recommend';
const API_ALL_ITEMS = 'http://127.0.0.1:5000/items';

console.log("UBC Social Spaces: Script Loading...");

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserver);
} else {
    startObserver();
}

function startObserver() {
    // Canvas menu ID is 'menu'
    const menu = document.getElementById('menu');
    if (menu) {
        initExtension(menu);
        return;
    }

    const observer = new MutationObserver((mutations, obs) => {
        const menu = document.getElementById('menu');
        if (menu) {
            initExtension(menu);
            obs.disconnect();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

function initExtension(globalNav) {
    if (document.getElementById('ubc-clubs-nav-item')) return;

    const navItem = document.createElement('li');
    navItem.id = 'ubc-clubs-nav-item';
    navItem.className = 'ic-app-header__menu-list-item'; 

    navItem.innerHTML = `
        <a id="global_nav_clubs_link" href="#" class="ic-app-header__menu-list-link">
            <div class="menu-item-icon-container" aria-hidden="true">
                <svg class="ic-icon-svg ic-icon-svg--dashboard" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3">
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

    // --- POSITIONING FIX ---
    const targetIndex = 3; 
    if (globalNav.children.length > targetIndex) {
        globalNav.insertBefore(navItem, globalNav.children[targetIndex]);
    } else {
        globalNav.appendChild(navItem);
    }
}

async function toggleTray() {
    let tray = document.getElementById('ubc-clubs-tray');
    let menutab = document.getElementById('ubc-clubs-nav-item');
    
    if (tray) {
        tray.classList.toggle('tray-open');
        menutab.classList.toggle('ic-app-header__menu-list-item--active');
        return;
    }

    try {
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
            menutab.classList.toggle('ic-app-header__menu-list-item--active');
        });

        // VIEW LOGIC
        if (localStorage.getItem('ubc_social_onboarded') === 'true') {
            showDashboard();
        } else {
            showOnboarding();
        }

        setupEventHandlers();

        // Animate In
        setTimeout(() => {
            document.getElementById('ubc-clubs-tray').classList.add('tray-open');
        }, 50);

    } catch (err) {
        console.error("❌ ERROR:", err);
    }
}

function setupEventHandlers() {
    const submitBtn = document.getElementById('ai-submit-btn');
    if(submitBtn) submitBtn.addEventListener('click', handleOnboardingSubmit);

    const redoBtn = document.getElementById('redo-onboarding-btn');
    if(redoBtn) redoBtn.addEventListener('click', () => {
        localStorage.removeItem('ubc_social_onboarded');
        showOnboarding();
    });

    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.nav-tab').forEach(t => {
                t.classList.remove('active');
            });
            tab.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            const target = document.getElementById(tab.dataset.target);
            if(target) target.style.display = 'block';
        });
    });
}

// --- VIEW CONTROLLERS ---

function showOnboarding() {
    const tray = document.getElementById('ubc-clubs-tray');
    tray.classList.remove('tray-full-width'); // Narrow width
    
    document.getElementById('view-onboarding').style.display = 'block';
    document.getElementById('view-dashboard').style.display = 'none';
}

function showDashboard() {
    const tray = document.getElementById('ubc-clubs-tray');
    tray.classList.add('tray-full-width'); // EXPAND TO FULL WIDTH
    
    document.getElementById('view-onboarding').style.display = 'none';
    document.getElementById('view-dashboard').style.display = 'flex';
    
    loadSchoolFeed();
    loadAllClubs();
    loadGroups();
}

// --- DATA LOADERS & AI ---

async function handleOnboardingSubmit() {
    const btn = document.getElementById('ai-submit-btn');
    btn.innerText = "Thinking...";
    
    const year = document.getElementById('ai-year').value;
    const classes = document.getElementById('ai-classes').value.split(',');
    const interests = document.getElementById('ai-interests').value;

    try {
        const res = await fetch(API_RECOMMEND, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({year, classes, interests})
        });
        const data = await res.json();
        renderAIResults(data);
        
        btn.innerText = "Enter Social Space ->";
        btn.onclick = () => {
            localStorage.setItem('ubc_social_onboarded', 'true');
            showDashboard();
        };

    } catch (e) {
        alert("Server error. Is Python running?");
        btn.innerText = "Retry";
    }
}

function renderAIResults(items) {
    const area = document.getElementById('ai-results-area');
    area.innerHTML = '<h4>✨ Recommended for You</h4>';
    items.forEach(item => {
        area.innerHTML += createCardHTML(item, true);
    });
}

// --- LOADERS WITH GRID SUPPORT ---

async function loadAllClubs() {
    const container = document.getElementById('all-clubs-list');
    if(!container) return;
    container.classList.add('grid-container'); // Add Grid Class
    
    const res = await fetch(API_ALL_ITEMS);
    const items = await res.json();
    container.innerHTML = '';
    items.forEach(item => {
        container.innerHTML += createCardHTML(item);
    });
}

function loadSchoolFeed() {
    // Note: School feed usually isn't a grid, keep it linear or grid as preferred
    fetch(API_ALL_ITEMS).then(res => res.json()).then(items => {
        const eventContainer = document.getElementById('feed-events');
        eventContainer.classList.add('grid-container'); // Add Grid Class
        const events = items.filter(i => i.category === 'Event');
        eventContainer.innerHTML = '';
        events.forEach(ev => {
            eventContainer.innerHTML += createCardHTML(ev);
        });
    });
}

function loadGroups() {
    fetch(API_ALL_ITEMS).then(res => res.json()).then(items => {
        const groupContainer = document.getElementById('available-group-chats');
        groupContainer.classList.add('grid-container'); // Add Grid Class
        const groups = items.filter(i => i.category === 'Group');
        groupContainer.innerHTML = '';
        groups.forEach(g => {
            groupContainer.innerHTML += createCardHTML(g);
        });
    });
}

function createCardHTML(item, showScore=false) {
    // Simplified card for grid view
    let tagColor = "#eee";
    if (item.category === "Club") tagColor = "#d1e7dd";
    if (item.category === "Event") tagColor = "#f8d7da";
    if (item.category === "Tech") tagColor = "#cff4fc";

    return `
        <div class="dashboard-card" style="height: 100%;">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h4 style="margin:0 0 10px 0;">${item.name}</h4>
                <span style="background:${tagColor}; padding:2px 8px; border-radius:12px; font-size:0.7em;">${item.category}</span>
            </div>
            <p style="font-size:0.9em; color:#555; flex-grow: 1;">${item.description.substring(0, 100)}...</p>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px; font-size:0.85em;">
                ${showScore ? `<strong style="color:green">${Math.round(item.match_score*100)}% Match</strong>` : `<a href="#">View Details</a>`}
            </div>
        </div>
    `;
}