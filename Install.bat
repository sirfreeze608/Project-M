@echo off
SETLOCAL EnableDelayedExpansion

SET "APP_NAME=Pacer+Mylang"
SET "INSTALL_DIR=%ProgramFiles%\%APP_NAME%"
SET "ICON_DIR=%INSTALL_DIR%\assets"
SET "SHORTCUT_PATH=%PUBLIC%\Desktop\%APP_NAME%.lnk"

:: ... [Keep directory creation and xcopy steps identical here] ...

echo Creating Headless Desktop shortcut...
SET "VBS_SCRIPT=%TEMP%\CreateShortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"

:: CRITICAL FIXES FOR NO TERMINAL LAUNCH:
:: 1. Explicitly target pythonw.exe instead of python.exe
echo oLink.TargetPath = "pythonw.exe" >> "%VBS_SCRIPT%"
:: 2. Pass the exact path to your main interface file
echo oLink.Arguments = """%INSTALL_DIR%\Pacer_mylang.py""" >> "%VBS_SCRIPT%"
:: 3. Set the working directory so your "mylang/" subfolder resolution doesn't break
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%VBS_SCRIPT%"

echo oLink.Description = "Launch %APP_NAME% (GUI Mode)" >> "%VBS_SCRIPT%"
if exist "%ICON_DIR%\icon.ico" (
    echo oLink.IconLocation = "%ICON_DIR%\icon.ico, 0" >> "%VBS_SCRIPT%"
)
echo oLink.Save >> "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"
echo Installation complete! Terminal-free shortcut created.
pause