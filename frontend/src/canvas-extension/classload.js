// Session token for authentication
const SESSION_TOKEN = 'qRrl-skZBpTUo3QSsb0QOexTda6HWVozH3AgfFQ7rfU';
const API_BASE = 'http://localhost:5000/api';

async function loadClasses() {
    try {
        const response = await fetch(`${API_BASE}/classes`, {
            headers: {
                'Authorization': `Bearer ${SESSION_TOKEN}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const classes = await response.json();
        console.log("Classes loaded:", classes);
        return classes;
    } catch (error) {
        console.error("Error loading classes:", error);
        return [];
    }
}

function createClassCard(classItem) {
    return `
        <div class="class-card" data-class-id="${classItem.id}">
            <div class="class-header">
                <h4 class="class-name">${classItem.name}</h4>
                <span class="class-badge">CLASS</span>
            </div>
            <div class="class-info">
                <p class="class-code">Course ID: ${classItem.id}</p>
                <p class="class-date">Added: ${new Date(classItem.created_at).toLocaleDateString()}</p>
            </div>
            <div class="class-actions">
                <button class="btn-open-chat" onclick="openClassChat(${classItem.id})">Open Chat</button>
                <button class="btn-view-details" onclick="viewClassDetails(${classItem.id})">Details</button>
            </div>
        </div>
    `;
}

async function displayClasses(containerId) {
    const classes = await loadClasses();
    const container = document.getElementById(containerId);

    if (!container) {
        console.error(`Container ${containerId} not found`);
        return;
    }

    if (classes.length === 0) {
        container.innerHTML = '<p class="no-data">No classes found</p>';
        return;
    }

    container.innerHTML = classes.map(classItem => createClassCard(classItem)).join('');
    return classes;
}

function openClassChat(classId) {
    console.log(`Opening chat for class ${classId}`);
}

function viewClassDetails(classId) {
    console.log(`Viewing details for class ${classId}`);
}
