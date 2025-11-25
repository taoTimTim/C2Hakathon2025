# UBC Canvas Connect

A Chrome/Firefox extension that brings real-time chat, club discovery, and intelligent recommendations directly into Canvas LMS, helping students connect with classmates and discover campus communities.

## Overview

UBC Canvas Connect transforms the Canvas learning management system into a social platform where students can communicate, collaborate, and discover opportunities. The extension seamlessly integrates into Canvas pages, adding a "Connect" button to the global navigation that opens an interface displaying university announcement, clubs, your personal classes, and chat channels to communicate with peers.

The app solves the problem of fragmented communication in online learning environments. Instead of switching between multiple platforms, students can chat with classmates directly within Canvas, discover clubs and events based on their interests and courses, and form study groups—all without leaving their learning environment.

What makes it unique is its deep Canvas integration: it automatically syncs courses and groups from Canvas, uses machine learning to recommend relevant clubs and events based on a student's academic profile, and provides real-time chat functionality. The system intelligently matches students with clubs , analyzing their year level, enrolled courses, and stated interests to provide personalized recommendations.

## Features

**Intelligent Club Recommendations** — Machine learning algorithm analyzes user profile (year level, courses, interests) to recommend relevant clubs and events from a curated database.

**Automatic Canvas Sync** — Seamlessly syncs Canvas courses and groups as chat rooms, automatically adding enrolled students as members without manual setup.

**Club Discovery and Management** — Browse and join student clubs, create new clubs, and manage memberships with role-based permissions (leaders, members).

**Personal Study Groups** — Create private study groups for focused collaboration outside of official course structures, and connect with your groups for group projects instead of using external applications.

**Announcements and Posts** — Share announcements and posts within classes, clubs, and project groups with support for images and rich content.

## Tech Stack

**Frontend:**
- HTML / CSS / JavaScript
- Chrome Extension (Manifest V3)
- Firefox Extension (Manifest V2)
- Content Scripts for Canvas page injection

**Backend:**
- Flask (main server)
- FastAPI (secondary backend for data operations)
- Flask-SocketIO (WebSocket support for real-time messaging)
- Python 3.x

**Database:**
- MySQL
- Consolidated schema supporting users, rooms, messages, clubs, and posts

**Other:**
- Canvas LMS API (for course/group sync and authentication)
- scikit-learn (TF-IDF vectorization for recommendation engine)
- pandas (data processing for recommendations)
- CORS-enabled API architecture

## Architecture

The system follows a multi-service architecture with clear separation of concerns:

**Extension Layer** - Content scripts inject UI into Canvas pages, background scripts handle API communication and keep-alive connections. The extension communicates with the Flask server via REST APIs.

**Flask Server (Port 5000)** - Handles authentication, Canvas API integration, and room management. Routes are organized into blueprints: auth, chat, canvas_sync, and recommendation.

**FastAPI Backend (Port 8000)** - Provides RESTful endpoints for data operations including users, rooms, classes, groups, clubs, messages, and posts. Uses Pydantic models for validation.

**Recommendation Service (Port 5001)** - Separate Flask service that loads clubs, events, and groups from database/CSV files, trains a TF-IDF model, and provides recommendation endpoints. Acts as a proxy for the main Flask API.

**Database Layer** - MySQL database with consolidated schema. Rooms table supports multiple types (class, club, project, personal) with a unified room_members table. Session tokens stored for authentication.

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd C2Hakathon2025
```

### 2. Backend setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set up environment variables. Create a `.env` file in the root directory:

```env
# Database Configuration
DB_NAME=your_database_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Canvas API Configuration
CANVAS_API_URL=https://canvas.ubc.ca/api/v1
CANVAS_BASE_URL=https://canvas.ubc.ca

# Server Configuration
PORT=5000
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:5000,https://canvas.ubc.ca

# Recommendation Service
RECOMMENDATION_URL=http://localhost:5001
FLASK_API_URL=http://127.0.0.1:5000

Start the Flask server (main backend):

```bash
cd server
python app.py
```

In a separate terminal, start the FastAPI backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

In another terminal, start the recommendation service:

```bash
cd backend
python recommendation_service.py
```

### 3. Extension setup

Build the manifest for your browser:

**For Chrome:**
```bash
cd frontend/src/canvas-extension
node build-manifest.js chrome
```

**For Firefox:**
```bash
cd frontend/src/canvas-extension
node build-manifest.js firefox
```

Load the extension:

1. Open Chrome and navigate to `chrome://extensions` (or Firefox: `about:debugging#/runtime/this-firefox`)
2. Enable "Developer Mode" (toggle in top right)
3. Click "Load unpacked" (Chrome) or "Load Temporary Add-on" (Firefox)
4. Select the `frontend/src/canvas-extension` folder

The extension should now appear in your extensions list. Navigate to `https://canvas.ubc.ca` and you should see a "Connect" button in the global navigation.

## How It Works

**Authentication Flow:** Users provide their Canvas API token through the extension. The Flask server validates the token with Canvas API, retrieves user information, creates/updates the user in the database, and generates a session token. This token is used for all subsequent API requests.

**Canvas Sync:** When a user logs in, the system automatically fetches their enrolled courses and groups from Canvas API. Each course becomes a "class" room, and each group becomes a "project" room. All enrolled students are automatically added as room members. This sync happens on login and can be manually triggered via the `/api/sync` endpoint.

**Recommendation Engine:** The recommendation service loads clubs, events, and groups from the database and CSV files. It creates a combined text "soup" from name, category, and description fields. Using scikit-learn's TF-IDF vectorizer, it converts this into a feature matrix. When a user requests recommendations, their profile (year, classes, interests) is vectorized and compared using cosine similarity. The top 5 matches with scores > 0 are returned.

**Database Structure:** The consolidated schema uses a single `rooms` table with a `room_type` field to distinguish between classes, clubs, projects, and personal rooms. The `room_members` table handles all membership relationships. This design simplifies queries and allows for flexible room types while maintaining referential integrity.

**Extension Integration:** Content scripts run on Canvas pages and inject the chat UI. The extension intercepts Canvas navigation and adds a "Connect" button. When clicked, it opens a sidebar. Background scripts handle API calls and maintain persistent connections to prevent service worker termination.

## Inspiration

We built this project to address the communication gap in online learning environments. Canvas LMS provides excellent tools for course management but lacks integrated social features. Students often struggle to connect with classmates, form study groups, or discover campus clubs relevant to their interests. We wanted to create a seamless experience where students could chat, collaborate, and discover opportunities without leaving their learning environment.

The pain point was clear: students were using multiple platforms (Discord, Messages, Instagram,  email) to communicate about courses, leading to fragmented conversations and missed connections. By integrating directly into Canvas, we eliminate the need to switch contexts and make communication a natural part of the learning workflow.

## Challenges We Faced

**CORS Configuration** — Getting the extension to communicate with localhost servers required extensive CORS configuration and handling preflight requests across multiple services.

**Service Worker Persistence** — Chrome Manifest V3 uses service workers that can be terminated, requiring keep-alive mechanisms and careful connection management.

**Canvas API Rate Limiting** — Syncing large numbers of courses and groups required implementing pagination and error handling for rate-limited requests.

**Multi-Browser Compatibility** — Supporting both Chrome (Manifest V3) and Firefox (Manifest V2) required maintaining separate manifest files and browser API compatibility layers.

## Accomplishments

- Successfully integrated a Chrome/Firefox extension with Canvas LMS, injecting UI seamlessly into existing pages
- Implemented automatic Canvas course and group synchronization, creating chat rooms without manual setup
- Developed a machine learning recommendation engine that provides personalized club suggestions
- Created a unified database schema supporting multiple room types (classes, clubs, projects, personal groups)
- Achieved multi-service architecture with Flask, FastAPI, and a separate recommendation service working in harmony
- Successfully handled browser extension limitations and service worker constraints

## What We Learned

**Extension Development** — Deep dive into Chrome Manifest V3 and Firefox Manifest V2 differences, content script injection, background service workers, and browser API compatibility.

**Machine Learning Integration** — Applying TF-IDF vectorization and cosine similarity for content-based recommendations, balancing model accuracy with real-time performance.

**API Design** — Creating RESTful endpoints with proper authentication, error handling, and CORS configuration for cross-origin requests from browser extensions.

**Database Design** — Consolidating multiple related tables into a unified schema while maintaining flexibility and referential integrity.

**Multi-Service Coordination** — Orchestrating multiple backend services (Flask, FastAPI, recommendation service) with proper proxy patterns and service communication.

**Canvas API Integration** — Working with Canvas LMS API, handling pagination, rate limits, and syncing complex data structures like courses, groups, and enrollments.

## Future Improvements

**Enhanced Recommendations** — Incorporate collaborative filtering, user interaction history, and more sophisticated ML models to improve recommendation accuracy.

**Mobile Support** — Develop mobile apps or a responsive web interface so students can access chat and recommendations on their phones.

**Notification System** — Implement push notifications for new messages, mentions, and club recommendations even when Canvas is not open.

**Rich Media Support** — Add file sharing, image uploads, and embedded content in chat messages and posts.

**Advanced Search** — Implement full-text search across messages, posts, and clubs with filtering and sorting options.

**Analytics Dashboard** — Provide insights into club engagement, message activity, and recommendation effectiveness for administrators.

**Security Enhancements** — Add end-to-end encryption for private messages, rate limiting on API endpoints, and more robust session management.

**UI/UX Polish** — Improve the chat interface with better message formatting, emoji support, read receipts, and typing indicators.

**Integration Expansion** — Support for other LMS platforms beyond Canvas, calendar integration for club events, and email notifications.

## Team

- Rowan Fortier
- Patrik Balazsy
- Timmi Draper
- Graeme Bradford
