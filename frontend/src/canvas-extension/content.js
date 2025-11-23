// Browser API compatibility (works for both Chrome and Firefox)
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// Keep background service worker alive with persistent connection
let keepAliveConnection = null;

function maintainBackgroundConnection() {
    try {
        // Create persistent connection to keep service worker alive
        keepAliveConnection = browserAPI.runtime.connect({ name: 'keepAlive' });
        
        keepAliveConnection.onDisconnect.addListener(() => {
            // Reconnect if connection is lost
            console.log('Background connection lost, reconnecting...');
            setTimeout(maintainBackgroundConnection, 1000);
        });
        
        // Send periodic pings to keep connection alive
        const pingInterval = setInterval(() => {
            if (keepAliveConnection) {
                try {
                    keepAliveConnection.postMessage({ action: 'ping' });
                } catch (e) {
                    clearInterval(pingInterval);
                    maintainBackgroundConnection();
                }
            }
        }, 20000); // Ping every 20 seconds
        
        console.log('Background connection established');
    } catch (error) {
        console.error('Failed to establish background connection:', error);
        // Retry after a delay
        setTimeout(maintainBackgroundConnection, 2000);
    }
}

// Establish connection when content script loads
maintainBackgroundConnection();

async function safeFetch(url, options = {}) {
    return new Promise((resolve, reject) => {
        // Ensure background script is ready
        try {
            browserAPI.runtime.sendMessage(
                { action: "fetch", url, options },
                (response) => {
                    // Check for runtime errors (e.g., background script not responding)
                    if (browserAPI.runtime.lastError) {
                        console.error('Background script error:', browserAPI.runtime.lastError);
                        return reject(browserAPI.runtime.lastError.message || "Background script error. Please reload the extension.");
                    }
                    if (!response) {
                        console.error('No response from background script');
                        return reject("No response received. Please reload the extension.");
                    }
                    if (response.error) return reject(response.error);
                    resolve(response.data);
                }
            );
        } catch (error) {
            console.error('Error sending message to background:', error);
            reject(error.message || "Failed to communicate with background script");
        }
    });
}


// ===========================================================
// ROBUST VERSION - Left Tray & Full Screen Dashboard
// ===========================================================

const API_RECOMMEND = 'http://127.0.0.1:5001/recommend';
const API_ALL_ITEMS = 'http://127.0.0.1:5001/items';
// Incoming features from teammate
const API_BASE = 'http://localhost:5000/api';
const SESSION_TOKEN = 'qRrl-skZBpTUo3QSsb0QOexTda6HWVozH3AgfFQ7rfU';

// COLORS (Your UI Fixes)
const COLOR_ACTIVE_BG = '#FFFFFF';      // White background when open
const COLOR_ACTIVE_ICON = 'rgb(9, 32, 67)'; // Exact UBC Blue RGB
const COLOR_INACTIVE_ICON = '#FFFFFF';  // White icon when closed
const COLOR_TEXT_ALWAYS_WHITE = '#FFFFFF'; // Ensures tooltip text stays white

// STATE TRACKER (To restore the previous menu state)
let previousState = {
    element: null,
    hadClass: false,
    ariaCurrent: null
};

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
    
    // FORCE FULL WIDTH/HEIGHT for the white background effect
    navItem.style.position = 'relative';
    navItem.style.width = '100%'; 
    navItem.style.margin = '0'; 
    navItem.style.boxSizing = 'border-box';

    navItem.innerHTML = `
        <a id="global_nav_clubs_link" href="#" class="ic-app-header__menu-list-link" style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-decoration: none; background: transparent !important; border: none !important;">
            <div class="menu-item-icon-container" aria-hidden="true" style="position: relative; z-index: 20; display: flex; align-items: center; justify-content: center; background: transparent !important; border: none !important; margin: 0 !important;">
                <svg class="ic-icon-svg ic-icon-svg--dashboard" xmlns="http://www.w3.org/2000/svg" height="26px" viewBox="0 -960 960 960" width="26px" fill="${COLOR_INACTIVE_ICON}" style="display: block; margin: 0 auto;">
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

    // --- SMART NAVIGATION GUARD ---
    globalNav.addEventListener('click', (e) => {
        if (navItem.contains(e.target)) return;

        const link = e.target.closest('a');
        if (!link) return;

        if (link.pathname === window.location.pathname) {
            e.preventDefault(); 
            e.stopPropagation();
            setMenuIconActive(false);
            const tray = document.getElementById('ubc-clubs-tray');
            if(tray) tray.classList.remove('tray-open');
        } else {
            handleExternalNavClick();
        }
    }, true); 
}

// --- HANDLER FOR REAL NAVIGATIONS ---
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

    previousState = { element: null, hadClass: false, ariaCurrent: null };
}

// --- ACTIVE STATE CONTROLLER ---
function setMenuIconActive(isActive) {
    const navItem = document.getElementById('ubc-clubs-nav-item');
    if (!navItem) return;

    const iconSvg = navItem.querySelector('svg');
    const text = navItem.querySelector('.menu-item__text'); 

    if (isActive) {
        // Active Style
        navItem.style.backgroundColor = COLOR_ACTIVE_BG; 
        if(iconSvg) {
            iconSvg.setAttribute('fill', COLOR_ACTIVE_ICON); 
            iconSvg.style.fill = COLOR_ACTIVE_ICON; 
        }
        if(text) text.style.setProperty('color', COLOR_ACTIVE_ICON, 'important');

        // Deactivate Others
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
        // Inactive Style
        navItem.style.backgroundColor = ''; 
        if(iconSvg) {
            iconSvg.setAttribute('fill', COLOR_INACTIVE_ICON); 
            iconSvg.style.fill = COLOR_INACTIVE_ICON;
        }
        if(text) text.style.setProperty('color', COLOR_TEXT_ALWAYS_WHITE, 'important');

        // Restore Previous State
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
    
    if (tray) {
        tray.classList.toggle('tray-open');
        const isOpen = tray.classList.contains('tray-open');
        setMenuIconActive(isOpen);
        return;
    }

    try {
        const url = browserAPI.runtime.getURL('canvas_connect.html');
        const html = await browserAPI.runtime.getURL('canvas_connect.html')
        ? await (await fetch(url)).text() 
        : ""; 

        const trayContainer = document.createElement('div');
        trayContainer.id = 'ubc-clubs-tray-container';
        trayContainer.innerHTML = html;
        document.body.appendChild(trayContainer);

        // Check if user is logged in
        const sessionToken = localStorage.getItem('ubc_session_token');
        if (!sessionToken) {
            // Show login view only
            const loginView = document.getElementById('view-login');
            const mainContent = document.getElementById('main-content');
            if (loginView) loginView.style.display = 'block';
            if (mainContent) mainContent.style.display = 'none';
            setupLoginHandler();
        } else {
            // User is logged in, show main content
            const loginView = document.getElementById('view-login');
            const mainContent = document.getElementById('main-content');
            
            if (loginView) loginView.style.display = 'none';
            if (mainContent) mainContent.style.display = 'block';
            
            // Close Handler
            const closeBtn = document.getElementById('ubc-tray-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
                    menutab.classList.toggle('ic-app-header__menu-list-item--active');
                });
            }
            
            // Logout Handler
            const logoutBtn = document.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', handleLogout);
            }

            // VIEW LOGIC
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
        }, 50);

    } catch (err) {
        console.error("ERROR:", err);
    }
}

function setupLoginHandler() {
    const loginBtn = document.getElementById('login-submit-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', handleLogin);
    }
    
    const tokenInput = document.getElementById('login-token');
    if (tokenInput) {
        tokenInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleLogin();
            }
        });
    }
}

function handleLogout() {
    // Clear session token
    localStorage.removeItem('ubc_session_token');
    
    // Reset tray to original size (remove full-width)
    const tray = document.getElementById('ubc-clubs-tray');
    if (tray) {
        tray.classList.remove('tray-full-width');
    }
    
    // Hide main content, show login
    const loginView = document.getElementById('view-login');
    const mainContent = document.getElementById('main-content');
    if (loginView) loginView.style.display = 'block';
    if (mainContent) mainContent.style.display = 'none';
    
    // Clear the token input field
    const tokenInput = document.getElementById('login-token');
    if (tokenInput) tokenInput.value = '';
    
    // Setup login handler again
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
        const response = await safeFetch('http://127.0.0.1:5000/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ canvas_token: canvasToken })
        });
        
        if (!response.session_token) {
            throw new Error('Invalid response from server');
        }
        
        // Store session token
        localStorage.setItem('ubc_session_token', response.session_token);
        
        // Hide login, show main content
        document.getElementById('view-login').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
        
        // Setup close handler
        document.getElementById('ubc-tray-close').addEventListener('click', () => {
            document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
            document.getElementById('ubc-clubs-nav-item').classList.toggle('ic-app-header__menu-list-item--active');
        });
        
        // Show onboarding or dashboard
        if (localStorage.getItem('ubc_social_onboarded') === 'true') {
            showDashboard();
        } else {
            showOnboarding();
        }
        
        setupEventHandlers();
        
    } catch (e) {
        errorDiv.textContent = e.message || 'Login failed. Please check your token.';
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
    tray.classList.add('tray-full-width'); // EXPAND TO FULL WIDTH
    
    document.getElementById('view-onboarding').style.display = 'none';
    document.getElementById('view-dashboard').style.display = 'flex';
    
    loadSchoolFeed();
    loadAllClubs();
    loadGroups();
    // Call teammate's new function
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
    area.innerHTML = '<h4>Recommended for You</h4>';
    items.forEach(item => {
        area.innerHTML += createCardHTML(item, true);
    });
}

// --- LOADERS WITH GRID SUPPORT ---

// New feature from teammate: Load Classes from backend
async function loadClasses() {
    try {
        // Get session token from localStorage (set during login)
        const sessionToken = localStorage.getItem('ubc_session_token');
        if (!sessionToken) {
            console.warn('No session token found, cannot load classes');
            const container = document.getElementById('all-classes-list');
            if (container) {
                container.innerHTML = '<p class="no-data">Please log in to view classes</p>';
            }
            return;
        }

        const classes = await safeFetch(`${API_BASE}/classes`, {
            headers: {
                'Authorization': `Bearer ${sessionToken}`,
                'Content-Type': 'application/json'
            }
        });

        console.log("Classes loaded:", classes);

        const container = document.getElementById('all-classes-list');
        // Safety check in case HTML for classes doesn't exist yet
        if (!container) {
            console.warn("Classes container not found");
            return; 
        }

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
        console.error("Error details:", {
            message: error.message,
            stack: error.stack,
            error: error
        });
        
        const container = document.getElementById('all-classes-list');
        if (container) {
            container.innerHTML = `<p class="no-data" style="color: red;">Error loading classes: ${error.message || error}</p>`;
        }
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
            <p style="font-size:0.85em; color:#777;">Added: ${new Date(classItem.created_at).toLocaleDateString()}</p>
            <div style="margin-top:10px; border-top:1px solid #eee; padding-top:5px;">
                <button class="btn-open-chat" onclick="openClassChat(${classItem.id})" style="margin-right:5px; padding:5px 10px; background:#2D3B45; color:white; border:none; border-radius:4px; cursor:pointer;">Open Chat</button>
                <button class="btn-view-details" onclick="viewClassDetails(${classItem.id})" style="padding:5px 10px; background:#555; color:white; border:none; border-radius:4px; cursor:pointer;">Details</button>
            </div>
        </div>
    `;
}

// Global functions required for inline onclick events
window.openClassChat = function(classId) {
    console.log(`Opening chat for class ${classId}`);
}

window.viewClassDetails = function(classId) {
    console.log(`Viewing details for class ${classId}`);
}

async function loadAllClubs() {
    const container = document.getElementById('all-clubs-list');
    if(!container) return;
    container.classList.add('grid-container'); 
    
    const items = await safeFetch(API_ALL_ITEMS);

    container.innerHTML = '';
    items.forEach(item => {
        container.innerHTML += createCardHTML(item);
    });
}

function loadSchoolFeed() {
    // Note: School feed usually isn't a grid, keep it linear or grid as preferred
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
    safeFetch(API_ALL_ITEMS).then(items => {
        const groupContainer = document.getElementById('available-group-chats');
        groupContainer.classList.add('grid-container'); 
        const groups = items.filter(i => i.category === 'Group');
        groupContainer.innerHTML = '';
        groups.forEach(g => {
            groupContainer.innerHTML += createCardHTML(g);
        });
    });
}

function createCardHTML(item, showScore=false) {
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