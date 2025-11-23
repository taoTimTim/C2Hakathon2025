// ===========================================================
// FINAL ROBUST VERSION - Fixed Re-Open Geometry & Missing Helpers
// ===========================================================

// Browser API compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// --- KEEP ALIVE LOGIC ---
let keepAliveConnection = null;

function maintainBackgroundConnection() {
    try {
        keepAliveConnection = browserAPI.runtime.connect({ name: 'keepAlive' });
        keepAliveConnection.onDisconnect.addListener(() => {
            // console.log('Background connection lost, reconnecting...');
            setTimeout(maintainBackgroundConnection, 1000);
        });
        const pingInterval = setInterval(() => {
            if (keepAliveConnection) {
                try {
                    keepAliveConnection.postMessage({ action: 'ping' });
                } catch (e) {
                    clearInterval(pingInterval);
                    maintainBackgroundConnection();
                }
            }
        }, 20000); 
        // console.log('Background connection established');
    } catch (error) {
        console.error('Failed to establish background connection:', error);
        setTimeout(maintainBackgroundConnection, 2000);
    }
}
maintainBackgroundConnection();

async function safeFetch(url, options = {}) {
    return new Promise((resolve, reject) => {
        try {
            browserAPI.runtime.sendMessage(
                { action: "fetch", url, options },
                (response) => {
                    if (browserAPI.runtime.lastError) {
                        return reject(browserAPI.runtime.lastError.message || "Background script error.");
                    }
                    if (!response) {
                        return reject("No response received.");
                    }
                    if (response.error) return reject(response.error);
                    resolve(response.data);
                }
            );
        } catch (error) {
            reject(error.message);
        }
    });
}

const API_RECOMMEND = 'http://127.0.0.1:5001/recommend';
const API_ALL_ITEMS = 'http://127.0.0.1:5001/items';
const API_BASE = 'http://127.0.0.1:5001/api'; // Using 5001 for Mac compat
const SESSION_TOKEN = 'qRrl-skZBpTUo3QSsb0QOexTda6HWVozH3AgfFQ7rfU';

// --- COLORS ---
const COLOR_ACTIVE_BG = '#FFFFFF';      
const COLOR_ACTIVE_ICON = 'rgb(9, 32, 67)'; 
const COLOR_INACTIVE_ICON = '#FFFFFF';  
const COLOR_TEXT_ALWAYS_WHITE = '#FFFFFF'; 

// --- STATE TRACKER ---
let previousState = {
    element: null,
    hadClass: false,
    ariaCurrent: null
};
let originalPageTitle = document.title;

console.log("UBC Social Spaces: Script Loading...");

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserver);
} else {
    startObserver();
}

function startObserver() {
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
    
    navItem.style.position = 'relative';
    navItem.style.width = '100%'; 
    navItem.style.margin = '0'; 
    navItem.style.boxSizing = 'border-box';

    navItem.innerHTML = `
        <a id="global_nav_clubs_link" href="#" class="ic-app-header__menu-list-link" style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; background: transparent !important; border: none !important;">
            <div class="menu-item-icon-container" aria-hidden="true" style="position: relative; z-index: 20; display: flex; align-items: center; justify-content: center; background: transparent !important; border: none !important; margin: 0 !important;">
                <svg class="ic-icon-svg ic-icon-svg--dashboard" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="${COLOR_INACTIVE_ICON}" style="display: block; margin: 0 auto;">
                    <path d="M160-120q-33 0-56.5-23.5T80-200v-560q0-33 23.5-56.5T160-840h560q33 0 56.5 23.5T800-760v80h80v80h-80v80h80v80h-80v80h80v80h-80v80q0 33-23.5 56.5T720-120H160Zm0-80h560v-560H160v560Zm80-80h200v-160H240v160Zm240-280h160v-120H480v120Zm-240 80h200v-200H240v200Zm240 200h160v-240H480v240ZM160-760v560-560Z"/>
                </svg>
            </div>
            <div class="menu-item__text" style="position: relative; z-index: 20; color: ${COLOR_TEXT_ALWAYS_WHITE} !important;">Connect</div>
        </a>
    `;

    navItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTray();
    });

    const targetIndex = 3; 
    if (globalNav.children.length > targetIndex) {
        globalNav.insertBefore(navItem, globalNav.children[targetIndex]);
    } else {
        globalNav.appendChild(navItem);
    }

    globalNav.addEventListener('click', (e) => {
        if (navItem.contains(e.target)) return;
        const link = e.target.closest('a');
        if (!link) return;

        if (link.pathname === window.location.pathname) {
            e.preventDefault(); 
            e.stopPropagation();
            setMenuIconActive(false);
            const tray = document.getElementById('ubc-clubs-tray');
            if(tray) {
                tray.classList.remove('tray-open');
                // Removed classList.remove('tray-full-width') to prevent shrinking bug
            }
            document.title = originalPageTitle;
        } else {
            handleExternalNavClick();
        }
    }, true); 
}

function handleExternalNavClick() {
    const tray = document.getElementById('ubc-clubs-tray');
    if (tray) {
        tray.classList.remove('tray-open');
    }
    
    const navItem = document.getElementById('ubc-clubs-nav-item');
    if(navItem) {
        const iconSvg = navItem.querySelector('svg');
        const text = navItem.querySelector('.menu-item__text');
        
        navItem.style.backgroundColor = ''; 
        if(iconSvg) {
            iconSvg.setAttribute('fill', COLOR_INACTIVE_ICON); 
            iconSvg.style.fill = COLOR_INACTIVE_ICON;
        }
        if(text) text.style.setProperty('color', COLOR_TEXT_ALWAYS_WHITE, 'important');
    }
    
    document.title = originalPageTitle;
    previousState = { element: null, hadClass: false, ariaCurrent: null };
}

function setMenuIconActive(isActive) {
    const navItem = document.getElementById('ubc-clubs-nav-item');
    if (!navItem) return;

    const iconSvg = navItem.querySelector('svg');
    const text = navItem.querySelector('.menu-item__text'); 

    if (isActive) {
        navItem.style.backgroundColor = COLOR_ACTIVE_BG; 
        if(iconSvg) {
            iconSvg.setAttribute('fill', COLOR_ACTIVE_ICON); 
            iconSvg.style.fill = COLOR_ACTIVE_ICON; 
        }
        if(text) text.style.setProperty('color', COLOR_ACTIVE_ICON, 'important');

        const menuItems = document.querySelectorAll('.ic-app-header__menu-list-item');
        menuItems.forEach(item => {
            if (item === navItem) return; 
            if (item.classList.contains('ic-app-header__menu-list-item--active')) {
                previousState.element = item;
                previousState.hadClass = true;
                previousState.ariaCurrent = null; 
                item.classList.remove('ic-app-header__menu-list-item--active');
            }
            const link = item.querySelector('a');
            if (link && link.getAttribute('aria-current') === 'page') {
                if (!previousState.element || previousState.element === item) {
                    previousState.element = item;
                    previousState.ariaCurrent = 'page';
                }
                link.removeAttribute('aria-current');
            }
        });
    } else {
        navItem.style.backgroundColor = ''; 
        if(iconSvg) {
            iconSvg.setAttribute('fill', COLOR_INACTIVE_ICON); 
            iconSvg.style.fill = COLOR_INACTIVE_ICON;
        }
        if(text) text.style.setProperty('color', COLOR_TEXT_ALWAYS_WHITE, 'important');

        if (previousState.element) {
            if (previousState.hadClass) {
                previousState.element.classList.add('ic-app-header__menu-list-item--active');
            }
            if (previousState.ariaCurrent) {
                const link = previousState.element.querySelector('a');
                if (link) link.setAttribute('aria-current', 'page');
            }
            previousState = { element: null, hadClass: false, ariaCurrent: null };
        }
    }
}

async function toggleTray() {
    let tray = document.getElementById('ubc-clubs-tray');
    
    // Case 1: Tray already exists
    if (tray) {
        const isNowOpen = tray.classList.toggle('tray-open');
        setMenuIconActive(isNowOpen);
        
        // FIX: Force re-check of width every time we open existing tray
        if (isNowOpen) {
            if (localStorage.getItem('ubc_social_onboarded') === 'true') {
                tray.classList.add('tray-full-width');
            }
            originalPageTitle = document.title;
            document.title = "Connect";
        } else {
            document.title = originalPageTitle;
        }
        return;
    }

    // Case 2: First load
    try {
        const url = browserAPI.runtime.getURL('canvas_connect.html');
        const html = await (await fetch(url)).text();

        const trayContainer = document.createElement('div');
        trayContainer.id = 'ubc-clubs-tray-container';
        trayContainer.innerHTML = html;
        document.body.appendChild(trayContainer);

        document.getElementById('ubc-tray-close').addEventListener('click', () => {
            document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
            setMenuIconActive(false);
            document.title = originalPageTitle;
        });

        const sessionToken = localStorage.getItem('ubc_session_token');
        if (!sessionToken) {
            const loginView = document.getElementById('view-login');
            const mainContent = document.getElementById('main-content');
            if(loginView) loginView.style.display = 'block';
            if(mainContent) mainContent.style.display = 'none';
            setupLoginHandler();
        } else {
            if (localStorage.getItem('ubc_social_onboarded') === 'true') {
                showDashboard();
            } else {
                showOnboarding();
            }
            setupEventHandlers();
        }

        setTimeout(() => {
            document.getElementById('ubc-clubs-tray').classList.add('tray-open');
            setMenuIconActive(true);
            originalPageTitle = document.title;
            document.title = "Connect";
        }, 50);

    } catch (err) {
        console.error("ERROR:", err);
    }
}

// ... (Rest of your logic: SetupLogin, Logout, etc.) ...
function setupLoginHandler() {
    const loginBtn = document.getElementById('login-submit-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', handleLogin);
    }
    const tokenInput = document.getElementById('login-token');
    if (tokenInput) {
        tokenInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleLogin();
        });
    }
}

function handleLogout() {
    localStorage.removeItem('ubc_session_token');
    const tray = document.getElementById('ubc-clubs-tray');
    if (tray) tray.classList.remove('tray-full-width');
    const loginView = document.getElementById('view-login');
    const mainContent = document.getElementById('main-content');
    if (loginView) loginView.style.display = 'block';
    if (mainContent) mainContent.style.display = 'none';
    const tokenInput = document.getElementById('login-token');
    if (tokenInput) tokenInput.value = '';
    setupLoginHandler();
}

async function handleLogin() {
    const tokenInput = document.getElementById('login-token');
    const loginBtn = document.getElementById('login-submit-btn');
    const errorDiv = document.getElementById('login-error');
    const canvasToken = tokenInput.value.trim();
    
    if (!canvasToken) {
        errorDiv.textContent = 'Please enter your Canvas API token';
        errorDiv.style.display = 'block';
        return;
    }
    
    loginBtn.innerText = 'Logging in...';
    loginBtn.disabled = true;
    errorDiv.style.display = 'none';
    
    try {
        const response = await safeFetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ canvas_token: canvasToken })
        });
        
        if (!response.session_token) throw new Error('Invalid response');
        localStorage.setItem('ubc_session_token', response.session_token);
        
        document.getElementById('view-login').style.display = 'none';
        if(document.getElementById('main-content')) document.getElementById('main-content').style.display = 'block';
        
        if (localStorage.getItem('ubc_social_onboarded') === 'true') {
            showDashboard();
        } else {
            showOnboarding();
        }
        setupEventHandlers();
        
    } catch (e) {
        errorDiv.textContent = e.message || 'Login failed.';
        errorDiv.style.display = 'block';
        loginBtn.innerText = 'Login';
        loginBtn.disabled = false;
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

function showOnboarding() {
    const tray = document.getElementById('ubc-clubs-tray');
    tray.classList.remove('tray-full-width'); 
    document.getElementById('view-onboarding').style.display = 'block';
    document.getElementById('view-dashboard').style.display = 'none';
}

function showDashboard() {
    const tray = document.getElementById('ubc-clubs-tray');
    tray.classList.add('tray-full-width'); 
    document.getElementById('view-onboarding').style.display = 'none';
    document.getElementById('view-dashboard').style.display = 'flex';
    loadSchoolFeed();
    loadAllClubs();
    loadGroups();
    loadClasses();
}

async function handleOnboardingSubmit() {
    const btn = document.getElementById('ai-submit-btn');
    btn.innerText = "Thinking...";
    const year = document.getElementById('ai-year').value;
    const classes = document.getElementById('ai-classes').value.split(',');
    const interests = document.getElementById('ai-interests').value;

    try {
        const data = await safeFetch(API_RECOMMEND, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ year, classes, interests })
        });
        renderAIResults(data);
        btn.innerText = "Enter Social Space";
        btn.onclick = () => {
            localStorage.setItem('ubc_social_onboarded', 'true');
            showDashboard();
        };
    } catch (e) {
        console.error(e);
        alert("Server error. Is Python running?");
        btn.innerText = "Retry";
    }
}

function renderAIResults(items) {
    const area = document.getElementById('ai-results-area');
    area.innerHTML = '<h4>Recommended for You</h4>';
    items.forEach(item => {
        area.innerHTML += createCardHTML(item, true);
    });
}

async function loadClasses() {
    try {
        const sessionToken = localStorage.getItem('ubc_session_token');
        if (!sessionToken) return; 
        const classes = await safeFetch(`${API_BASE}/classes`, {
            headers: { 'Authorization': `Bearer ${sessionToken}`, 'Content-Type': 'application/json' }
        });
        const container = document.getElementById('all-classes-list');
        if (!container) return;
        container.classList.add('grid-container');
        container.innerHTML = '';
        if (!classes || classes.length === 0) {
            container.innerHTML = '<p class="no-data">No classes found</p>';
            return;
        }
        classes.forEach(classItem => {
            container.innerHTML += createClassCard(classItem);
        });
    } catch (error) {
        console.error("Error loading classes:", error);
    }
}

function createClassCard(classItem) {
    return `
        <div class="dashboard-card class-card" data-class-id="${classItem.id}">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h4 style="margin:0 0 10px 0;">${classItem.name}</h4>
                <span style="background:#d1e7dd; padding:2px 8px; border-radius:12px; font-size:0.7em;">CLASS</span>
            </div>
            <p style="font-size:0.9em; color:#555;">Course ID: ${classItem.id}</p>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px;">
                <button class="btn-open-chat" onclick="openClassChat(${classItem.id})" style="margin-right:5px; padding:5px 10px; background:#2D3B45; color:white; border:none; border-radius:4px; cursor:pointer;">Open Chat</button>
            </div>
        </div>
    `;
}

async function loadAllClubs() {
    const container = document.getElementById('all-clubs-list');
    if(!container) return;
    container.classList.add('grid-container'); 
    try {
        const items = await safeFetch(API_ALL_ITEMS);
        container.innerHTML = '';
        items.forEach(item => {
            container.innerHTML += createCardHTML(item);
        });
    } catch (e) { console.error("Error loading clubs", e); }
}

function loadSchoolFeed() {
    safeFetch(API_ALL_ITEMS).then(items => {
        const eventContainer = document.getElementById('feed-events');
        eventContainer.classList.add('grid-container'); 
        const events = items.filter(i => i.category === 'Event');
        eventContainer.innerHTML = '';
        events.forEach(ev => {
            eventContainer.innerHTML += createCardHTML(ev);
        });
    });
}

function loadGroups() {
    safeFetch(API_ALL_ITEMS).then(async (items) => {
        const groupContainer = document.getElementById('available-group-chats');
        groupContainer.classList.add('grid-container'); 
        const groups = items.filter(i => i.category === 'Group');
        groupContainer.innerHTML = '';
        groups.forEach(g => {
            groupContainer.innerHTML += createGroupCard(g, false);
        });
        
        // Attach event listeners to join buttons after HTML is inserted
        groupContainer.querySelectorAll('[data-join-group-id]').forEach(button => {
            const groupId = parseInt(button.getAttribute('data-join-group-id'));
            button.addEventListener('click', () => {
                if (window.joinGroup) {
                    window.joinGroup(groupId);
                } else {
                    console.error('joinGroup function not defined');
                }
            });
        });
    });
}

function createGroupCard(group, isJoined) {
    const badgeColor = '#fff3cd'; 
    const badgeText = 'GROUP';

    return `
        <div class="dashboard-card group-card" data-group-id="${group.id}">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h4 style="margin:0 0 10px 0;">${group.name}</h4>
                <span style="background:${badgeColor}; padding:2px 8px; border-radius:12px; font-size:0.7em;">${badgeText}</span>
            </div>
            <p style="font-size:0.9em; color:#555; margin:0 0 10px 0;">
                ${group.description || 'No description'}
            </p>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px;">
                ${isJoined
                    ? `<button style="padding:5px 10px; background:#2D3B45; color:white; border:none; border-radius:4px; cursor:pointer;">Open Chat</button>`
                    : `<button data-join-group-id="${group.id}" class="join-group-btn" style="padding:5px 10px; background:#0055B7; color:white; border:none; border-radius:4px; cursor:pointer;">Join Group</button>`
                }
            </div>
        </div>
    `;
}

function createCardHTML(item, showScore=false) {
    let tagColor = "#eee";
    if (item.category === "Club") tagColor = "#d1e7dd";
    if (item.category === "Event") tagColor = "#f8d7da";
    if (item.category === "Tech") tagColor = "#cff4fc";
    const uniqueId = `desc-${Math.floor(Math.random() * 100000)}`;

    return `
        <div class="dashboard-card" style="height: 100%; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h4 style="margin:0 0 10px 0;">${item.name}</h4>
                <span style="background:${tagColor}; padding:2px 8px; border-radius:10px; font-size:0.7em;">${item.category}</span>
            </div>
            <div style="flex-grow: 1;">
                <p id="${uniqueId}" class="desc-preview" style="font-size:0.9em; color:#555; margin:0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                    ${item.description}
                </p>
                <span onclick="document.getElementById('${uniqueId}').style.display = document.getElementById('${uniqueId}').style.display === 'block' ? '-webkit-box' : 'block'" class="read-more-link" style="color:#0055B7; font-size:0.8em; cursor:pointer; text-decoration:underline; margin-top:5px; display:inline-block;">Read description</span>
            </div>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px; font-size:0.85em;">
                ${showScore ? `<strong style="color:green">${Math.round(item.match_score*100)}% Match</strong>` : `<a href="#" style="color:#0055B7;">View Details</a>`}
            </div>
        </div>
    `;
}

// --- MISSING HELPERS ADDED BACK ---
window.openGroupChat = function(groupId) { console.log(`Opening chat for group ${groupId}`); alert(`Opening chat for group ${groupId}`); };

// Define joinGroup function on window object early
window.joinGroup = async function(groupId) {
    const sessionToken = localStorage.getItem('ubc_session_token');
    if (!sessionToken) {
        showNotification('Please log in first', 'error');
        return;
    }
    
    // Get group name for notification (from the DOM) - get it before we make the API call
    const groupCard = document.querySelector(`[data-group-id="${groupId}"]`);
    let groupName = 'group';
    if (groupCard) {
        const nameEl = groupCard.querySelector('h4');
        if (nameEl) groupName = nameEl.textContent;
    }
    
    try {
        // The backend will extract user_id from the Authorization header automatically
        const url = `${API_BASE}/groups/${groupId}/join`;
        console.log('Joining group:', groupId, 'URL:', url);
        
        const response = await safeFetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // Backend will add user_id from the auth token
        });
        
        console.log('Join group response:', response);
        
        // Show success notification
        const name = response.group_name || groupName;
        showNotification(`You joined the group ${name}`, 'success');
        
        // Reload groups to update UI
        loadGroups();
    } catch (e) {
        console.error("Error joining group:", e);
        console.error("Error details:", {
            message: e.message,
            stack: e.stack,
            name: e.name
        });
        showNotification(`Failed to join group: ${e.message || 'Please try again.'}`, 'error');
    }
};

// Helper to get current user_id from session token
async function getCurrentUserId() {
    const sessionToken = localStorage.getItem('ubc_session_token');
    if (!sessionToken) return null;
    
    try {
        const response = await safeFetch(`${API_BASE}/auth/verify`, {
            headers: { 'Authorization': `Bearer ${sessionToken}` }
        });
        return response.user_id || response.canvas_user_id;
    } catch (e) {
        console.error("Error getting user ID:", e);
        return null;
    }
}

// Show notification at bottom of screen
function showNotification(message, type = 'success') {
    // Remove existing notification if any
    const existing = document.getElementById('ubc-notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.id = 'ubc-notification';
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#0055B7' : '#d32f2f'};
        color: white;
        padding: 12px 24px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        animation: slideUp 0.3s ease-out;
    `;
    notification.textContent = message;
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideUp {
            from {
                transform: translateX(-50%) translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }
        }
    `;
    if (!document.getElementById('ubc-notification-styles')) {
        style.id = 'ubc-notification-styles';
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

window.openClassChat = function(classId) { console.log(`Opening chat ${classId}`); };
window.viewClassDetails = function(classId) { console.log(`Details ${classId}`); };