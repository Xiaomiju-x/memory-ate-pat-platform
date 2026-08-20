@echo off
setlocal EnableExtensions

cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js 22.12 or newer is required.
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm is required. Install an official Node.js distribution.
  exit /b 1
)

echo [1/3] Installing locked dependencies...
if not exist "package-lock.json" (
  echo [ERROR] package-lock.json is required for a reproducible build.
  exit /b 1
)
call npm ci
if errorlevel 1 exit /b 1

echo [2/3] Running automated tests...
call npm test
if errorlevel 1 exit /b 1

echo [3/3] Building the Windows x64 portable executable...
call npm run portable
if errorlevel 1 exit /b 1

echo.
echo Build complete. See the single EXE in: %CD%\dist
endlocal
