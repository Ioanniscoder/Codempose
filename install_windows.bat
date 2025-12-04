@echo off
REM Windows Installation Script for Codempose
REM This script helps with common Windows installation issues

echo ==========================================
echo Codempose Windows Installation
echo ==========================================
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Fix file attributes on critical files
echo.
echo [2/5] Fixing file attributes...
attrib -h -s -r studies\_study_path.py 2>nul
attrib -h -s -r studies\__init__.py 2>nul
attrib -h -s -r src\__init__.py 2>nul

REM Verify critical files exist
echo.
echo [3/5] Verifying installation files...
if not exist "studies\_study_path.py" (
    echo ERROR: studies\_study_path.py missing!
    echo This file is required for the framework to work.
    echo.
    echo Please re-extract the distribution tarball.
    echo See INSTALL_WINDOWS.md for instructions.
    pause
    exit /b 1
)
echo    OK: studies\_study_path.py found

if not exist "src\score_builder.py" (
    echo ERROR: src\score_builder.py missing!
    pause
    exit /b 1
)
echo    OK: src\score_builder.py found

REM Install dependencies
echo.
echo [4/5] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some packages failed to install
    echo You may need to install them manually
    pause
)

REM Test import
echo.
echo [5/5] Testing framework imports...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from studies import _study_path; from src import score_builder; print('OK: All imports successful')"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Import test failed
    echo See error message above
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo You can now run studies:
echo    python studies\eightyfirst.py
echo    python studies\102th.py
echo.
echo To create a new study:
echo    python generate_study.py
echo.
pause
