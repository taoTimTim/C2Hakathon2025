@echo off
REM Auto-setup script for Windows

if "%1"=="" (
    echo Which browser are you using?
    echo 1) Chrome
    echo 2) Firefox
    set /p choice="Enter choice (1 or 2): "
    
    if "%choice%"=="1" (
        set BROWSER=chrome
    ) else if "%choice%"=="2" (
        set BROWSER=firefox
    ) else (
        echo Invalid choice. Defaulting to Chrome.
        set BROWSER=chrome
    )
) else (
    set BROWSER=%1
)

echo Building manifest for %BROWSER%...
node build-manifest.js %BROWSER%

echo.
echo Setup complete! Your manifest.json is now configured for %BROWSER%
echo Next steps:
if "%BROWSER%"=="chrome" (
    echo    1. Open chrome://extensions/
    echo    2. Enable 'Developer mode'
    echo    3. Click 'Load unpacked'
    echo    4. Select this folder: %CD%
) else (
    echo    1. Open about:debugging
    echo    2. Click 'This Firefox'
    echo    3. Click 'Load Temporary Add-on'
    echo    4. Select manifest.json from: %CD%
)

