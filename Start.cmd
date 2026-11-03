@echo off
setlocal
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
  echo Install Python 3.10 or newer from https://www.python.org/downloads/
  echo Enable Add Python to PATH, then run this file again.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Setting up your PC helper...
  python -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m ensurepip --upgrade
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import yt_dlp, imageio_ffmpeg, yt_dlp_ejs" >nul 2>&1
if errorlevel 1 (
  echo Installing download tools. This may take a few minutes the first time.
  ".venv\Scripts\python.exe" -m pip install --upgrade "yt-dlp[default]" imageio-ffmpeg
  if errorlevel 1 goto failed
)
set "PATH=%~dp0tools;%PATH%"
".venv\Scripts\python.exe" setup_runtime.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" helper.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Could not start Playlist Saver. Check the message above.
pause
exit /b 1
