@echo off
echo Building New QR2Key (x64)
echo =========================

REM Define project root and venv path
set PROJECT_ROOT=%~dp0
set VENV_PATH=%PROJECT_ROOT%venv-x64

echo Project root: %PROJECT_ROOT%
echo Venv path: %VENV_PATH%

REM Create and activate virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment. Make sure Python is installed and in PATH.
        goto end_error
    )
)

echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    goto end_error
)

REM Install dependencies
echo Installing common dependencies from requirements.txt...
pip install -r "%PROJECT_ROOT%requirements.txt"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install common dependencies.
    goto end_error
)

REM Install Windows-specific dependencies
echo Installing Windows-specific dependencies from requirements-win.txt...
pip install -r "%PROJECT_ROOT%requirements-win.txt"
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install Windows-specific dependencies.
    goto end_error
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install PyInstaller.
    goto end_error
)

REM Build with PyInstaller
echo Building with PyInstaller...
pyinstaller --noconfirm --clean --onefile --name QR2Key-App ^
    --hidden-import=serial.tools.list_ports ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32con ^
    "%PROJECT_ROOT%qr2key\main.py"

IF %ERRORLEVEL% NEQ 0 (
    echo PyInstaller build failed.
    goto end_error
)

echo PyInstaller build completed. Executable should be in dist\QR2Key-App.exe
goto end_success

:end_error
echo.
echo Build process failed.
goto end_script

:end_success
echo.
echo Build process completed successfully.
goto end_script

:end_script
echo.
if defined VIRTUAL_ENV (
    echo Deactivating virtual environment...
    deactivate
)
echo Script finished.
pause 