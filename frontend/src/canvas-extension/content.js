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
const API_BASE = 'http://localhost:5000/api'; // Main backend on port 5000
const SESSION_TOKEN = 'qRrl-skZBpTUo3QSsb0QOexTda6HWVozH3AgfFQ7rfU';

// Expose globally for chat-ui.js
window.safeFetch = safeFetch;
window.API_BASE = API_BASE;

// --- COLORS ---
const COLOR_ACTIVE_BG = '#FFFFFF';
const COLOR_ACTIVE_ICON = 'rgb(9, 32, 67)';
const COLOR_INACTIVE_ICON = '#FFFFFF';
const COLOR_TEXT_ALWAYS_WHITE = '#FFFFFF';

// Global functions for onclick handlers (must be defined early)
window.openClassChat = function(classId, className, roomType) {
    console.log(`Opening chat for class ${classId}`);
    if (typeof openChat === 'function') {
        openChat(classId, className, roomType);
    } else {
        console.error('openChat function not available yet');
    }
};

window.viewClassDetails = function(classId) {
    console.log(`Viewing details for class ${classId}`);
};

window.openGroupChat = function(groupId, groupName, roomType) {
    console.log(`Opening chat for group ${groupId}`);
    if (typeof openChat === 'function') {
        openChat(groupId, groupName, roomType);
    } else {
        console.error('openChat function not available yet');
    }
};

window.joinGroup = function(groupId) {
    console.log(`Joining group ${groupId}`);
};

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
                <svg xmlns="http://www.w3.org/2000/svg" height="48px" viewBox="0 -960 960 960" width="48px" fill="#e3e3e3"><path d="M169.62-140q-23.53 0-40.61-17.08-17.09-17.08-17.09-40.61v-564.62q0-23.53 17.09-40.61Q146.09-820 169.62-820h564.61q23.53 0 40.61 17.08t17.08 40.61v68.47h56.16v45.38h-56.16v145.77h56.16v45.38h-56.16v145.77h56.16v45.38h-56.16v68.47q0 23.53-17.08 40.61T734.23-140H169.62Zm0-45.39h564.61q4.62 0 8.46-3.84 3.85-3.85 3.85-8.46v-564.62q0-4.61-3.85-8.46-3.84-3.84-8.46-3.84H169.62q-4.62 0-8.47 3.84-3.84 3.85-3.84 8.46v564.62q0 4.61 3.84 8.46 3.85 3.84 8.47 3.84Zm68.46-80.77h219.53v-169.99H238.08v169.99ZM498-575.62h167.77v-118.22H498v118.22Zm-259.92 99.08h219.53v-217.3H238.08v217.3ZM498-266.16h167.77v-269.07H498v269.07ZM157.31-774.61v589.22-589.22Z"/></svg>
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

        // Attach UI event handlers immediately so onboarding controls
        // (like the AI submit button) work even when the login view
        // is shown or other conditional views are active.
        setupEventHandlers();

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

    // Event delegation for chat buttons
    document.addEventListener('click', (e) => {
        // Handle class chat buttons
        if (e.target.classList.contains('btn-open-chat')) {
            const classId = e.target.dataset.classId;
            const className = e.target.dataset.className;
            const roomType = e.target.dataset.roomType;
            if (classId && className && roomType) {
                window.openClassChat(classId, className, roomType);
            }
        }

        // Handle group chat buttons
        if (e.target.classList.contains('btn-open-group-chat')) {
            const groupId = e.target.dataset.groupId;
            const groupName = e.target.dataset.groupName;
            const roomType = e.target.dataset.roomType;
            if (groupId && groupName && roomType) {
                window.openGroupChat(groupId, groupName, roomType);
            }
        }

        // Handle join group buttons
        if (e.target.classList.contains('btn-join-group')) {
            const groupId = e.target.dataset.groupId;
            if (groupId) {
                window.joinGroup(groupId);
            }
        }

        // Handle view class details buttons
        if (e.target.classList.contains('btn-view-details')) {
            const classId = e.target.dataset.classId;
            if (classId) {
                window.viewClassDetails(classId);
            }
        }
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
    const escapedName = classItem.name.replace(/'/g, "\\'");
    return `
        <div class="dashboard-card class-card" data-class-id="${classItem.id}">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h4 style="margin:0 0 10px 0;">${classItem.name}</h4>
                <span style="background:#d1e7dd; padding:2px 8px; border-radius:12px; font-size:0.7em;">CLASS</span>
            </div>
            <p style="font-size:0.9em; color:#555;">Course ID: ${classItem.id}</p>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px;">
                <button class="btn-open-chat" data-class-id="${classItem.id}" data-class-name="${escapedName}" data-room-type="class" style="margin-right:5px; padding:5px 10px; background:#2D3B45; color:white; border:none; border-radius:4px; cursor:pointer;">Open Chat</button>
                <button class="btn-view-details" data-class-id="${classItem.id}" style="padding:5px 10px; background:#555; color:white; border:none; border-radius:4px; cursor:pointer;">Details</button>
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
        try {
            const groupContainer = document.getElementById('available-group-chats');
            groupContainer.classList.add('grid-container');
            const groups = items.filter(i => i.category === 'Group');
            groupContainer.innerHTML = '';
            groups.forEach(g => {
                groupContainer.innerHTML += createCardHTML(g);
            });

            // Get session token from localStorage
            const sessionToken = localStorage.getItem('ubc_session_token');
            if (!sessionToken) {
                console.warn('No session token found, cannot load groups');
                return;
            }

            // Fetch rooms for the user
            const rooms = await safeFetch(`${API_BASE}/rooms`, {
                headers: {
                    'Authorization': `Bearer ${sessionToken}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log("Rooms loaded:", rooms);

            // Filter for project and personal rooms (groups)
            const groupRooms = rooms.filter(r => r.room_type === 'project' || r.room_type === 'personal');

            // Display joined groups
            const joinedContainer = document.getElementById('my-joined-chats');
            if (joinedContainer) {
                if (groupRooms.length === 0) {
                    joinedContainer.innerHTML = '<p style="color:grey; font-style:italic;">You haven\'t joined any groups yet.</p>';
                } else {
                    joinedContainer.innerHTML = '';
                    groupRooms.forEach(group => {
                        joinedContainer.innerHTML += createGroupCard(group, true);
                    });
                }
            }

            // Load all available groups
            const allGroups = await safeFetch(`${API_BASE}/groups`, {
                headers: {
                    'Authorization': `Bearer ${sessionToken}`,
                    'Content-Type': 'application/json'
                }
            });
            console.log("All groups loaded:", allGroups);

            // Filter out groups the user is already in
            const joinedIds = new Set(groupRooms.map(g => g.id));
            const availableGroups = allGroups.filter(g => !joinedIds.has(g.id));

            // Display available groups
            const availableContainer = document.getElementById('available-group-chats');
            if (availableContainer) {
                availableContainer.classList.add('grid-container');

                if (availableGroups.length === 0) {
                    availableContainer.innerHTML = '<p class="no-data">No available groups</p>';
                } else {
                    availableContainer.innerHTML = '';
                    availableGroups.forEach(group => {
                        availableContainer.innerHTML += createGroupCard(group, false);
                    });
                }
            }
        } catch (error) {
            console.error("Error loading groups:", error);
        }
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
    const badgeColor = group.room_type === 'personal' ? '#cff4fc' : '#fff3cd';
    const badgeText = group.room_type === 'personal' ? 'PERSONAL' : 'PROJECT';
    const escapedName = group.name.replace(/'/g, "\\'");
    const uniqueId = `desc-group-${group.id || Math.random().toString(36).substr(2, 9)}`;

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
                    ? `<button class="btn-open-group-chat" data-group-id="${group.id}" data-group-name="${escapedName}" data-room-type="${group.room_type}" style="padding:5px 10px; background:#2D3B45; color:white; border:none; border-radius:4px; cursor:pointer;">Open Chat</button>`
                    : `<button class="btn-join-group" data-group-id="${group.id}" style="padding:5px 10px; background:#0374B5; color:white; border:none; border-radius:4px; cursor:pointer;">Join Group</button>`
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
