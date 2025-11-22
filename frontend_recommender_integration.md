/**
 * Fetches AI recommendations based on user profile.
 * * @param {string} year - e.g. "1st Year", "Grad Student"
 * @param {Array} classes - e.g. ["COSC 101", "MATH 200"]
 * @param {string} interests - e.g. "I love hiking and chess"
 * @returns {Promise<Array>} - Returns an array of club/event objects
 */
async function getSocialRecommendations(year, classes, interests) {
    const API_URL = "http://localhost:5000/recommend";

    const payload = {
        year: year,
        classes: classes,
        interests: interests
    };

    try {
        console.log("📡 Sending data to AI:", payload);
        
        const response = await fetch(API_URL, {
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
        console.log("AI Recommendations received:", data);
        return data;

    } catch (error) {
        console.error("AI Connection Failed:", error);
        // Fallback: If server is down, return empty list so app doesn't crash
        return [];
    }
}

// === EXAMPLE USAGE ===
// Call this function when the user clicks "Next" on your form.
/*
getSocialRecommendations("1st Year", ["COSC 101"], "I like coding")
    .then(results => {
        // 'results' is your array of clubs/events.
        // Loop through it and display them in your UI.
        console.log(results); 
    });
*/