# UBC Canvas Club Connector Extension

Chrome and Firefox extension for connecting UBC Canvas students with clubs and communities.

## 🚀 Quick Start (Super Simple!)

### Chrome Users
**Just load the extension!** The `manifest.json` is already configured for Chrome.

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `frontend/src/canvas-extension/` folder

### Firefox Users
**Just rename one file!**

1. Rename `manifest.firefox.json` to `manifest.json` (backup the old one first if you want)
2. Open `about:debugging`
3. Click "This Firefox" (left sidebar)
4. Click "Load Temporary Add-on"
5. Select `manifest.json` from the `frontend/src/canvas-extension/` folder

That's it! No scripts to run, no commands to type. 🎉

---

## 🔧 Advanced: Build Scripts (Optional)

If you want to use the automated build system instead:

### Windows
```bash
setup.bat
```

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Or use NPM
```bash
npm run build:chrome    # For Chrome
npm run build:firefox   # For Firefox
```

## Loading the Extension

### Chrome
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `frontend/src/canvas-extension/` folder

### Firefox
1. Open `about:debugging`
2. Click "This Firefox" (left sidebar)
3. Click "Load Temporary Add-on"
4. Select `frontend/src/canvas-extension/manifest.json`

## Development

Before making changes, run the build script for your browser:
- Chrome: `npm run build:chrome`
- Firefox: `npm run build:firefox`

The extension will automatically work with both browsers once you run the appropriate build command.

