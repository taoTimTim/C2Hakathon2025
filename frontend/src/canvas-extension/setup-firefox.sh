#!/bin/bash

# Quick Firefox setup - just run this!
cd "$(dirname "$0")"

if [ -f "manifest.firefox.json" ]; then
    # Backup Chrome manifest if it exists
    if [ -f "manifest.json" ]; then
        mv manifest.json manifest.chrome.json
        echo "✅ Backed up Chrome manifest to manifest.chrome.json"
    fi
    
    # Use Firefox manifest
    cp manifest.firefox.json manifest.json
    echo "✅ Firefox manifest is now active!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Open about:debugging in Firefox"
    echo "   2. Click 'This Firefox' (left sidebar)"
    echo "   3. Click 'Load Temporary Add-on'"
    echo "   4. Select manifest.json from: $(pwd)"
else
    echo "❌ Error: manifest.firefox.json not found!"
    exit 1
fi

