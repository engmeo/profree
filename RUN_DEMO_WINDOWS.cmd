@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" "http://localhost:8000"
  py -3 -m http.server 8000
  goto :end
)
where python >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" "http://localhost:8000"
  python -m http.server 8000
  goto :end
)
echo Python 3 not found. Install Python 3, then run this file again.
pause
:end
