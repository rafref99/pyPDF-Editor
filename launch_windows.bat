@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
    goto :python_found
)

where python >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=python"
    goto :python_found
)

echo Python 3 is required but was not found.
echo Install Python from https://www.python.org/downloads/ and run this launcher again.
pause
exit /b 1

:python_found
if not exist ".venv" (
    echo Creating local Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Failed to create the Python virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo Checking and installing requirements...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo Starting pyPDF Editor...
"%VENV_PYTHON%" main.py
if errorlevel 1 (
    echo The app closed with an error.
    pause
    exit /b 1
)

endlocal
