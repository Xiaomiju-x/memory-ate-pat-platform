@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"

echo =====================================================
echo  AT24C02 PAT Generator - Reproducible Windows Build
echo =====================================================
echo.

set "PYTHON_CMD="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo [ERROR] Python 3 was not found. Install Python 3.10 or newer.
    goto :failed
)

%PYTHON_CMD% -c "import sys; raise SystemExit(0 if sys.version_info ^>= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10 or newer is required.
    %PYTHON_CMD% --version
    goto :failed
)

for %%F in (
    at24c02_pat_generator.py AT24C02_PAT_Generator_v8.0.0.spec
    requirements.txt requirements-dev.txt
) do if not exist "%%F" (
    echo [ERROR] Required file is missing: %%F
    goto :failed
)

echo [1/4] Installing pinned runtime and build dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt -r requirements-dev.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    goto :failed
)

echo [2/4] Running regression tests...
%PYTHON_CMD% -m unittest discover -s tests -v
if errorlevel 1 (
    echo [ERROR] Regression tests failed. Build stopped.
    goto :failed
)

echo [3/4] Building the executable from the checked-in spec...
%PYTHON_CMD% -m PyInstaller --clean --noconfirm "AT24C02_PAT_Generator_v8.0.0.spec"
if errorlevel 1 (
    echo [ERROR] PyInstaller failed. Review the output above.
    goto :failed
)

if not exist "dist\AT24C02_PAT_Generator_v8.0.0.exe" (
    echo [ERROR] Build finished without the expected executable.
    goto :failed
)

echo [4/4] Build complete.
echo Output: %CD%\dist\AT24C02_PAT_Generator_v8.0.0.exe
exit /b 0

:failed
echo.
echo Build did not complete.
exit /b 1
