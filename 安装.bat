@echo off
setlocal

:: Create and move to a clean directory
set "install_dir=%~dp0Pure-Yoga-Helper"
if not exist "%install_dir%" mkdir "%install_dir%"
cd "%install_dir%"

:: Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed, installing...

    :: Check if winget is available (Windows 10/11)
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Installing Git using winget...
        winget install --id Git.Git -e --source winget
    ) else (
        echo Winget is not installed, please manually install Git from https://git-scm.com/download/win
        cd ..
        pause
        exit /b 1
    )
)

:: Git is installed, check if this is a git repository
echo Git is installed. Checking repository...

if not exist ".git" (
    echo Git repository not found, starting clone...
    git clone https://github.com/JinyanYi/Pure-Yoga-Booking-Helper.git .
    if %errorlevel% neq 0 (
        echo Failed to clone repository!
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Updating repository...
    git fetch --all
    git reset --hard origin/main
    git pull origin main
)

echo Code update complete!

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed, please install Python first!
    cd ..
    pause
    exit /b 1
)

:: Install required packages if requirements.txt exists
if exist "requirements.txt" (
    echo Installing Python packages...
    pip install -r requirements.txt
)

echo Installation complete, starting booking program...
python start_booking.py

cd ..
pause