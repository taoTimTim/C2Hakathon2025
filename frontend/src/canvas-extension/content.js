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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
            </div>
            <div class="menu-item__text">Clubs</div>
        </a>
    `;

    // 4. Add Click Event
    navItem.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTray();
    });

    // 5. Append to the menu
    globalNav.appendChild(navItem);
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