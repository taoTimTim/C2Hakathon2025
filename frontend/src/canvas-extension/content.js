// Configuration
// REPLACE THIS with your actual endpoint later
const API_ENDPOINT = 'https://jsonplaceholder.typicode.com/posts?_limit=3'; 

console.log("UBC Club Extension: Loading...");

function initExtension() {
    // 1. Find the Global Navigation Menu (The unordered list in the blue bar)
    const globalNav = document.getElementById('menu');

    // Safety check: if we are on a page without the nav (e.g. login), stop.
    if (!globalNav) return;

    // 2. Prevent duplicate injection if the script runs twice
    if (document.getElementById('ubc-clubs-nav-item')) return;

    // 3. Create the List Item (li) and Link (a)
    const navItem = document.createElement('li');
    navItem.id = 'ubc-clubs-nav-item';
    navItem.className = 'ic-app-header__menu-list-item'; // Native Canvas class

    // Create the inner HTML for the button (Icon + Text)
    // We use a simple SVG for the icon
    navItem.innerHTML = `
        <a id="global_nav_clubs_link" href="#" class="ic-app-header__menu-list-link">
            <div class="menu-item-icon-container" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M160-120q-33 0-56.5-23.5T80-200v-560q0-33 23.5-56.5T160-840h560q33 0 56.5 23.5T800-760v80h80v80h-80v80h80v80h-80v80h80v80h-80v80q0 33-23.5 56.5T720-120H160Zm0-80h560v-560H160v560Zm80-80h200v-160H240v160Zm240-280h160v-120H480v120Zm-240 80h200v-200H240v200Zm240 200h160v-240H480v240ZM160-760v560-560Z"/></svg>
            </div>
            <div class="menu-item__text">Connect</div>
        </a>
    `;

    // 4. Add Click Event
    navItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTray();
    });

    // 5. Append to the menu
    globalNav.insertBefore(navItem, globalNav.childNodes[6]);
}

// Function to handle the Slide-out Tray
async function toggleTray() {
    // Check if tray already exists
    let tray = document.getElementById('ubc-clubs-tray');
    
    if (tray) {
        // Toggle visibility if it exists
        tray.classList.toggle('tray-open');
        return;
    }

    // If tray doesn't exist, create it from the HTML template
    const url = chrome.runtime.getURL('canvas_connect.html');
    const response = await fetch(url);
    const html = await response.text();

    const trayContainer = document.createElement('div');
    trayContainer.id = 'ubc-clubs-tray-container';
    trayContainer.innerHTML = html;
    document.body.appendChild(trayContainer);

    // Add close button logic
    document.getElementById('ubc-tray-close').addEventListener('click', () => {
        document.getElementById('ubc-clubs-tray').classList.remove('tray-open');
    });

    // Fetch and populate data
    fetchDataAndRender();
    
    // Slight delay to allow DOM to paint before sliding in
    setTimeout(() => {
        document.getElementById('ubc-clubs-tray').classList.add('tray-open');
    }, 50);
}

// Function to fetch data from API
function fetchDataAndRender() {
    const listContainer = document.getElementById('ubc-clubs-list');
    listContainer.innerHTML = '<p>Loading recommendations...</p>';

    fetch(API_ENDPOINT)
        .then(response => response.json())
        .then(data => {
            listContainer.innerHTML = ''; // Clear loading text
            
            // Map over your data (Assuming data is an array of objects)
            // You will need to adjust 'item.title' and 'item.body' to match your actual API JSON structure
            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'club-card';
                card.innerHTML = `
                    <h4>${item.title.substring(0, 20)}...</h4>
                    <p>${item.body.substring(0, 50)}...</p>
                    <button>Join Event</button>
                `;
                listContainer.appendChild(card);
            });
        })
        .catch(err => {
            console.error(err);
            listContainer.innerHTML = '<p style="color:red;">Failed to load events.</p>';
        });
}

// Run script
initExtension();