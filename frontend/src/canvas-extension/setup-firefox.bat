@echo off
REM Quick Firefox setup for Windows - just double-click this!

cd /d "%~dp0"

if exist "manifest.firefox.json" (
    REM Backup Chrome manifest if it exists
    if exist "manifest.json" (
        move manifest.json manifest.chrome.json
        echo ✅ Backed up Chrome manifest to manifest.chrome.json
    )
    
    REM Use Firefox manifest
    copy manifest.firefox.json manifest.json
    echo ✅ Firefox manifest is now active!
    echo.
    echo 📝 Next steps:
    echo    1. Open about:debugging in Firefox
    echo    2. Click 'This Firefox' (left sidebar)
    echo    3. Click 'Load Temporary Add-on'
    echo    4. Select manifest.json from: %CD%
) else (
    echo ❌ Error: manifest.firefox.json not found!
    pause
    exit /b 1
)

pause

