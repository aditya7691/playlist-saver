@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Open Start.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade "yt-dlp[default]" imageio-ffmpeg
pause
