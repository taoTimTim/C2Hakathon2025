#!/bin/bash

# Auto-detect browser or ask user
if [ "$1" != "" ]; then
    BROWSER=$1
else
    echo "Which browser are you using?"
    echo "1) Chrome"
    echo "2) Firefox"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            BROWSER="chrome"
            ;;
        2)
            BROWSER="firefox"
            ;;
        *)
            echo "Invalid choice. Defaulting to Chrome."
            BROWSER="chrome"
            ;;
    esac
fi

echo "Building manifest for $BROWSER..."
node build-manifest.js $BROWSER

echo ""
echo "✅ Setup complete! Your manifest.json is now configured for $BROWSER"
echo "📝 Next steps:"
if [ "$BROWSER" == "chrome" ]; then
    echo "   1. Open chrome://extensions/"
    echo "   2. Enable 'Developer mode'"
    echo "   3. Click 'Load unpacked'"
    echo "   4. Select this folder: $(pwd)"
else
    echo "   1. Open about:debugging"
    echo "   2. Click 'This Firefox'"
    echo "   3. Click 'Load Temporary Add-on'"
    echo "   4. Select manifest.json from: $(pwd)"
fi

