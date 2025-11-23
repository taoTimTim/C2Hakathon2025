#!/usr/bin/env node

/**
 * Build script to generate the correct manifest.json based on browser
 * Usage: node build-manifest.js [chrome|firefox]
 * Default: chrome
 */

const fs = require('fs');
const path = require('path');

const browser = process.argv[2] || 'chrome';

const chromeManifest = {
  "manifest_version": 3,
  "name": "UBC Canvas Club Connector",
  "version": "1.1",
  "description": "Adds a Clubs button to the global navigation and fetches recommendations.",
  "permissions": [
    "storage",
    "scripting",
    "alarms"
  ],
  "host_permissions": [
    "http://127.0.0.1:5000/*",
    "http://localhost:5000/*",
    "https://canvas.ubc.ca/*",
    "https://*.ubc.ca/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["https://canvas.ubc.ca/*"],
      "js": ["chat-client.js", "chat-ui.js", "content.js"],
      "css": ["styles.css"],
      "run_at": "document_idle"
    }
  ],
  "web_accessible_resources": [
    {
      "resources": ["canvas_connect.html"],
      "matches": ["<all_urls>"]
    }
  ]
};

const firefoxManifest = {
  "manifest_version": 2,
  "name": "UBC Canvas Club Connector",
  "version": "1.1",
  "description": "Adds a Clubs button to the global navigation and fetches recommendations.",
  "permissions": [
    "storage",
    "https://canvas.ubc.ca/*",
    "https://*.ubc.ca/*",
    "http://127.0.0.1:5000/*",
    "http://localhost:5000/*"
  ],
  "background": {
    "scripts": ["background.js"],
    "persistent": false
  },
  "content_scripts": [
    {
      "matches": ["https://canvas.ubc.ca/*"],
      "js": ["chat-client.js", "chat-ui.js", "content.js"],
      "css": ["styles.css"],
      "run_at": "document_idle"
    }
  ],
  "web_accessible_resources": [
    "canvas_connect.html"
  ],
  "browser_specific_settings": {
    "gecko": {
      "id": "ubc-canvas-club-connector@example.com"
    }
  }
};

const manifestDir = __dirname;
const manifestPath = path.join(manifestDir, 'manifest.json');

let manifest;
if (browser === 'firefox') {
  manifest = firefoxManifest;
  console.log('✅ Building Firefox manifest...');
} else {
  manifest = chromeManifest;
  console.log('✅ Building Chrome manifest...');
}

fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
console.log(`✅ manifest.json generated for ${browser}`);
console.log(`📁 Location: ${manifestPath}`);

